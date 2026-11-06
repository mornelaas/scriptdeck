from fastapi import FastAPI

from .routers import creators, scripts

app = FastAPI()

app.include_router(scripts.router)
app.include_router(creators.router)


@app.get("/")
def read_root() -> dict[str, str]:
    """Check that the ScriptDeck API is running."""
    return {"message": "Hello Scriptdeck"}
