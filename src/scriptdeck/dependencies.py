from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from .orm.models import Creator, Script
from .orm.session import get_db

SessionDep = Annotated[Session, Depends(get_db)]


def get_script_or_404(script_id: int, db: SessionDep) -> Script:
    """Load the script with this id, or stop the request with a 404."""
    script = db.get(Script, script_id)
    if script is None:
        raise HTTPException(status_code=404, detail="Script not found")
    return script


ScriptDep = Annotated[Script, Depends(get_script_or_404)]


def get_creator_or_404(creator_id: int, db: SessionDep) -> Creator:
    """Load the creator with this id, or stop the request with a 404."""
    creator = db.get(Creator, creator_id)
    if creator is None:
        raise HTTPException(status_code=404, detail="Creator not found")
    return creator


CreatorDep = Annotated[Creator, Depends(get_creator_or_404)]
