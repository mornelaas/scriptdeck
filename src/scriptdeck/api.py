from typing import Any

from fastapi import FastAPI, HTTPException

from .read_scripts import get_script

app = FastAPI()


@app.get("/")
def read_root() -> dict[str, str]:
    """Check that the ScriptDeck API is running."""
    return {"message": "Hello Scriptdeck"}


@app.get("/scripts/{script_id}")
def read_script(script_id: int) -> dict[str, Any]:
    """Return a single script by its id."""
    script = get_script(script_id)
    if script is None:
        raise HTTPException(status_code=404, detail="Script not found")
    return dict(script)
