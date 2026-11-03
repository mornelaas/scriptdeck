from typing import Any

from fastapi import FastAPI, HTTPException

from .create_creators import create_creator
from .create_scripts import create_script
from .read_creators import get_creator, list_creators
from .read_scripts import get_script, list_scripts
from .schemas import CreatorCreate, CreatorOut, ScriptCreate, ScriptOut, ScriptUpdate
from .update_delete import delete_script, update_script

app = FastAPI()


@app.get("/")
def read_root() -> dict[str, str]:
    """Check that the ScriptDeck API is running."""
    return {"message": "Hello Scriptdeck"}


@app.get("/scripts", response_model=list[ScriptOut])
def read_scripts(
    status: str | None = None,
    creator_id: int | None = None,
    platform: str | None = None,
) -> list[dict[str, Any]]:
    """Return all scripts, optionally filtered by status, creator and platform."""
    rows = list_scripts(status=status, creator_id=creator_id, platform=platform)
    scripts = []
    for row in rows:
        scripts.append(dict(row))
    return scripts


@app.get("/scripts/{script_id}", response_model=ScriptOut)
def read_script(script_id: int) -> dict[str, Any]:
    """Return a single script by its id."""
    script = get_script(script_id)
    if script is None:
        raise HTTPException(status_code=404, detail="Script not found")
    return dict(script)


@app.get("/creators", response_model=list[CreatorOut])
def read_creators() -> list[dict[str, Any]]:
    """Return all creators"""
    rows = list_creators()
    creators = []
    for row in rows:
        creators.append(dict(row))
    return creators


@app.get("/creators/{creator_id}/scripts", response_model=list[ScriptOut])
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


@app.post("/scripts", response_model=ScriptOut, status_code=201)
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


@app.post("/creators", response_model=CreatorOut, status_code=201)
def create_a_creator(creator: CreatorCreate) -> dict[str, Any]:
    """Create a new creator."""

    new_id = create_creator(
        name=creator.name,
        niche=creator.niche,
        handle=creator.handle,
    )
    created = get_creator(new_id)

    return dict(created)


@app.patch("/scripts/{script_id}", response_model=ScriptOut)
def update_a_script(script_id: int, changes: ScriptUpdate) -> dict[str, Any]:
    """Update only the fields the client sends."""
    current = get_script(script_id)
    if current is None:
        raise HTTPException(status_code=404, detail="Script not found")
    if changes.creator_id is not None and get_creator(changes.creator_id) is None:
        raise HTTPException(status_code=422, detail="Creator not found")

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


@app.put("/scripts/{script_id}", response_model=ScriptOut)
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


@app.delete("/scripts/{script_id}", status_code=204)
def delete_a_script(script_id: int) -> None:
    """Delete a full script."""
    deleted = delete_script(script_id=script_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Script not found")
