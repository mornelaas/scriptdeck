"""Business operations on scripts, shared by the API and the CLI."""

from sqlalchemy.orm import Session

from .models import can_transition
from .orm.models import Creator, Script
from .schemas import ScriptUpdate


class CreatorNotFoundError(Exception):
    """Raised when a creator_id does not match any creator."""


class InvalidTransitionError(Exception):
    """Raised when a status change breaks the script state machine."""


def update_script(db: Session, script: Script, changes: ScriptUpdate) -> Script:
    """Apply only the fields that were sent, following the business rules."""

    if changes.creator_id is not None and db.get(Creator, changes.creator_id) is None:
        raise CreatorNotFoundError(f"Creator {changes.creator_id} not found")

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
