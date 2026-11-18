from collections.abc import Sequence

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from scriptdeck.models import is_valid_handle

from ..dependencies import CreatorDep, SessionDep
from ..orm.models import Creator, Script
from ..schemas import CreatorCreate, CreatorOut, CreatorUpdate, ScriptOut

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
def create_a_creator(creator: CreatorCreate, db: SessionDep) -> Creator:
    """Create a new creator."""
    new_creator = Creator(**creator.model_dump())
    db.add(new_creator)
    db.commit()
    db.refresh(new_creator)
    return new_creator


@router.patch("/{creator_id}", response_model=CreatorOut, status_code=200)
def update_a_creator(
    creator: CreatorDep, changes: CreatorUpdate, db: SessionDep
) -> Creator:
    """Update only the fields the client sends."""

    if changes.handle is not None:
        if not is_valid_handle(changes.handle):
            raise HTTPException(
                status_code=422,
                detail="Handle must start with @",
            )

    for field, value in changes.model_dump(exclude_unset=True).items():
        setattr(creator, field, value)

    db.commit()
    db.refresh(creator)
    return creator
