from collections.abc import Sequence
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from ..create_creators import create_creator
from ..dependencies import SessionDep
from ..orm.models import Creator, Script
from ..read_creators import get_creator
from ..schemas import CreatorCreate, CreatorOut, ScriptOut

router = APIRouter(prefix="/creators", tags=["creators"])


@router.get("", response_model=list[CreatorOut])
def read_creators(db: SessionDep, niche: str | None = None) -> Sequence[Creator]:
    """Return all creators, optionally filtered by niche."""
    stmt = select(Creator).order_by(Creator.id)
    if niche is not None:
        stmt = stmt.where(Creator.niche == niche)
    return db.scalars(stmt).all()


@router.get("/{creator_id}/scripts", response_model=list[ScriptOut])
def read_creator_scripts(creator_id: int, db: SessionDep) -> list[Script]:
    """Return all scripts of a creator."""
    creator = db.get(Creator, creator_id)
    if creator is None:
        raise HTTPException(status_code=404, detail="Creator not found")
    return creator.scripts


@router.post("", response_model=CreatorOut, status_code=201)
def create_a_creator(creator: CreatorCreate) -> dict[str, Any]:
    """Create a new creator."""

    new_id = create_creator(
        name=creator.name,
        niche=creator.niche,
        handle=creator.handle,
    )
    created = get_creator(new_id)

    return dict(created)
