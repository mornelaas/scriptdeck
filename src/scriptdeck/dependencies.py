from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from .orm.models import Script
from .orm.session import get_db

SessionDep = Annotated[Session, Depends(get_db)]


def get_script_or_404(script_id: int, db: SessionDep) -> Script:
    """Load the script with this id, or stop the request with a 404."""
    script = db.get(Script, script_id)
    if script is None:
        raise HTTPException(status_code=404, detail="Script not found")
    return script


ScriptDep = Annotated[Script, Depends(get_script_or_404)]
