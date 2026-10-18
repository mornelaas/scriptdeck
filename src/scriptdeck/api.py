from typing import Any

from fastapi import FastAPI, HTTPException

from .read_creators import list_creators
from .read_scripts import get_script, list_scripts

app = FastAPI()


@app.get("/")
def read_root() -> dict[str, str]:
    """Check that the ScriptDeck API is running."""
    return {"message": "Hello Scriptdeck"}


@app.get("/scripts")
def read_scripts(
    status: str | None = None, creator_id: int | None = None
) -> list[dict[str, Any]]:
    """Return all scripts, optionally filtered by status and creator."""
    rows = list_scripts(status, creator_id)
    scripts = []
    for row in rows:
        scripts.append(dict(row))
    return scripts


@app.get("/scripts/{script_id}")
def read_script(script_id: int) -> dict[str, Any]:
    """Return a single script by its id."""
    script = get_script(script_id)
    if script is None:
        raise HTTPException(status_code=404, detail="Script not found")
    return dict(script)


@app.get("/creators")
def read_creators() -> list[dict[str, Any]]:
    """Return all creators"""
    rows = list_creators()
    creators = []
    for row in rows:
        creators.append(dict(row))
    return creators
