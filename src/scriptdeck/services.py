"""Business operations on scripts, shared by the API and the CLI."""

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from scriptdeck.security import hash_password

from .models import ScriptStatus, can_transition
from .orm.models import Creator, Script, User
from .schemas import ScriptCreate, ScriptUpdate, UserCreate


class CreatorNotFoundError(Exception):
    """Raised when a creator_id does not match any creator."""


class InvalidTransitionError(Exception):
    """Raised when a status change breaks the script state machine."""


class EmailAlreadyRegisteredError(Exception):
    """Raised when someone tries to register an email that is already in use."""


def _ensure_creator_exists(db: Session, creator_id: int | None) -> None:
    """Raise CreatorNotFoundError if creator_id points to no creator."""
    if creator_id is not None and db.get(Creator, creator_id) is None:
        raise CreatorNotFoundError(f"Creator {creator_id} not found")


def update_script(db: Session, script: Script, changes: ScriptUpdate) -> Script:
    """Apply only the fields that were sent, following the business rules."""

    _ensure_creator_exists(db, changes.creator_id)

    if changes.status is not None:
        allowed = can_transition(script.status, changes.status)
        if not allowed:
            raise InvalidTransitionError(
                f"Cannot move from '{script.status.value}' to '{changes.status.value}'"
            )

    sent_fields = changes.model_dump(exclude_unset=True)

    for field, value in sent_fields.items():
        setattr(script, field, value)

    db.commit()
    db.refresh(script)

    return script


def delete_script(db: Session, script: Script) -> None:
    """Delete the given script from the database."""
    db.delete(script)
    db.commit()


def create_script(db: Session, data: ScriptCreate) -> Script:
    """Create a script. It always starts in the 'idea' status."""
    _ensure_creator_exists(db, data.creator_id)

    script = Script(**data.model_dump())

    db.add(script)
    db.commit()
    db.refresh(script)

    return script


def list_scripts(
    db: Session,
    status: ScriptStatus | None = None,
    creator_id: int | None = None,
    platform: str | None = None,
) -> Sequence[Script]:
    """Return all scripts, optionally filtered by status, creator and platform."""
    stmt = select(Script).order_by(Script.id)
    if status is not None:
        stmt = stmt.where(Script.status == status)
    if creator_id is not None:
        stmt = stmt.where(Script.creator_id == creator_id)
    if platform is not None:
        stmt = stmt.where(Script.platform == platform)
    return db.scalars(stmt).all()


def count_scripts_by_status(db: Session) -> dict[ScriptStatus, int]:
    """Return how many scripts there are in each status."""
    stmt = (
        select(Script.status, func.count())
        .group_by(Script.status)
        .order_by(Script.status)
    )

    counts: dict[ScriptStatus, int] = {}

    for status, count in db.execute(stmt):
        counts[status] = count

    return counts


def count_scripts_by_creator(db: Session) -> dict[int | None, int]:
    """Return how many scripts each creator has (None means no creator)."""
    stmt = (
        select(Script.creator_id, func.count())
        .group_by(Script.creator_id)
        .order_by(Script.creator_id.nulls_first())
    )

    counts: dict[int | None, int] = {}

    for creator_id, count in db.execute(stmt):
        counts[creator_id] = count

    return counts


def _get_user_by_email(db: Session, email: str) -> User | None:
    """Return the user with this email, or None if there is none."""
    return db.scalar(select(User).where(User.email == email))


def register_user(db: Session, data: UserCreate) -> User:
    """Create a user with a hashed password, unless the email is already registered."""
    existing_user = _get_user_by_email(db=db, email=data.email.lower())

    if existing_user is not None:
        raise EmailAlreadyRegisteredError(
            f"This email: {existing_user.email} is already in use."
        )

    user = User(email=data.email.lower(), hashed_password=hash_password(data.password))

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
