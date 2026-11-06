from typing import Any

from fastapi import APIRouter, HTTPException

from ..create_creators import create_creator
from ..read_creators import get_creator, list_creators
from ..read_scripts import list_scripts
from ..schemas import CreatorCreate, CreatorOut, ScriptOut

router = APIRouter(prefix="/creators", tags=["creators"])


@router.get("", response_model=list[CreatorOut])
def read_creators() -> list[dict[str, Any]]:
    """Return all creators"""
    rows = list_creators()
    creators = []
    for row in rows:
        creators.append(dict(row))
    return creators


@router.get("/{creator_id}/scripts", response_model=list[ScriptOut])
def read_creator_scripts(creator_id: int) -> list[dict[str, Any]]:
    """Return all scripts of a creator."""
    creator = get_creator(creator_id)
    if creator is None:
        raise HTTPException(status_code=404, detail="Creator not found")

    rows = list_scripts(creator_id=creator_id)  # keyword argument
    creator_scripts = []
    for row in rows:
        creator_scripts.append(dict(row))
    return creator_scripts


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
