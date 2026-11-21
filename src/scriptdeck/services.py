"""Business operations on scripts, shared by the API and the CLI."""

from sqlalchemy.orm import Session

from .models import can_transition
from .orm.models import Creator, Script
from .schemas import ScriptCreate, ScriptUpdate


class CreatorNotFoundError(Exception):
    """Raised when a creator_id does not match any creator."""


class InvalidTransitionError(Exception):
    """Raised when a status change breaks the script state machine."""


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
