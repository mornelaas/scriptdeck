from collections.abc import Sequence
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from ..create_scripts import create_script
from ..dependencies import SessionDep
from ..models import ScriptStatus, can_transition
from ..orm.models import Script
from ..read_creators import get_creator
from ..read_scripts import get_script
from ..schemas import ScriptCreate, ScriptOut, ScriptUpdate
from ..update_delete import delete_script, update_script

router = APIRouter(prefix="/scripts", tags=["scripts"])


@router.get("", response_model=list[ScriptOut])
def read_scripts(
    db: SessionDep,
    status: str | None = None,
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


@router.get("/{script_id}", response_model=ScriptOut)
def read_script(script_id: int, db: SessionDep) -> Script:
    """Return a single script by its id."""
    script = db.get(Script, script_id)
    if script is None:
        raise HTTPException(status_code=404, detail="Script not found")
    return script


@router.post("", response_model=ScriptOut, status_code=201)
def create_a_script(script: ScriptCreate) -> dict[str, Any]:
    """Create a new script. It always starts in the 'idea' status."""
    if script.creator_id is not None and get_creator(script.creator_id) is None:
        raise HTTPException(status_code=422, detail="Creator not found")
    new_id = create_script(
        title=script.title,
        platform=script.platform,
        hook=script.hook,
        notes=script.notes,
        creator_id=script.creator_id,
    )
    created = get_script(new_id)

    return dict(created)


@router.put("/{script_id}", response_model=ScriptOut)
def replace_a_script(script_id: int, script: ScriptCreate) -> dict[str, Any]:
    """Replace the whole content of a script. The status is kept as it is."""
    current = get_script(script_id)
    if current is None:
        raise HTTPException(status_code=404, detail="Script not found")
    if script.creator_id is not None and get_creator(script.creator_id) is None:
        raise HTTPException(status_code=422, detail="Creator not found")

    update_script(
        script_id=script_id,
        title=script.title,
        status=current["status"],
        platform=script.platform,
        hook=script.hook,
        notes=script.notes,
        creator_id=script.creator_id,
    )
    updated = get_script(script_id)
    return dict(updated)


@router.patch("/{script_id}", response_model=ScriptOut)
def update_a_script(script_id: int, changes: ScriptUpdate) -> dict[str, Any]:
    """Update only the fields the client sends."""
    current = get_script(script_id)
    if current is None:
        raise HTTPException(status_code=404, detail="Script not found")
    if changes.creator_id is not None and get_creator(changes.creator_id) is None:
        raise HTTPException(status_code=422, detail="Creator not found")

    if changes.status is not None:
        current_status = ScriptStatus(current["status"])
        if not can_transition(current_status, changes.status):
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Cannot move from '{current_status.value}' "
                    f"to '{changes.status.value}'"
                ),
            )

    data = dict(current) | changes.model_dump(mode="json", exclude_unset=True)
    update_script(
        script_id=script_id,
        title=data["title"],
        status=data["status"],
        platform=data["platform"],
        hook=data["hook"],
        notes=data["notes"],
        creator_id=data["creator_id"],
    )
    updated = get_script(script_id)
    return dict(updated)


@router.delete("/{script_id}", status_code=204)
def delete_a_script(script_id: int) -> None:
    """Delete a full script."""
    deleted = delete_script(script_id=script_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Script not found")
