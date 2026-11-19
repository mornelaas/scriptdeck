from collections.abc import Sequence

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from ..dependencies import ScriptDep, SessionDep
from ..orm.models import Creator, Script
from ..schemas import ScriptCreate, ScriptOut, ScriptUpdate
from ..services import CreatorNotFoundError, InvalidTransitionError, update_script

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
def create_a_script(script: ScriptCreate, db: SessionDep) -> Script:
    """Create a new script. It always starts in the 'idea' status."""
    if script.creator_id is not None and db.get(Creator, script.creator_id) is None:
        raise HTTPException(status_code=422, detail="Creator not found")
    new_script = Script(**script.model_dump())
    db.add(new_script)
    db.commit()
    db.refresh(new_script)
    return new_script


@router.put("/{script_id}", response_model=ScriptOut)
def replace_a_script(script: ScriptDep, data: ScriptCreate, db: SessionDep) -> Script:
    """Replace the whole content of a script. The status is kept as it is."""
    if data.creator_id is not None and db.get(Creator, data.creator_id) is None:
        raise HTTPException(status_code=422, detail="Creator not found")
    for field, value in data.model_dump().items():
        setattr(script, field, value)
    db.commit()
    db.refresh(script)
    return script


@router.patch("/{script_id}", response_model=ScriptOut)
def update_a_script(script: ScriptDep, changes: ScriptUpdate, db: SessionDep) -> Script:
    """Update only the fields the client sends."""
    try:
        return update_script(db, script, changes)
    except CreatorNotFoundError as error:
        raise HTTPException(status_code=422, detail="Creator not found") from error
    except InvalidTransitionError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.delete("/{script_id}", status_code=204)
def delete_a_script(script: ScriptDep, db: SessionDep) -> None:
    """Delete a full script."""
    db.delete(script)
    db.commit()
