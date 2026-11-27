from fastapi import FastAPI

from .routers import auth, creators, scripts

app = FastAPI()

app.include_router(scripts.router)
app.include_router(creators.router)
app.include_router(auth.router)


@app.get("/")
def read_root() -> dict[str, str]:
    """Check that the ScriptDeck API is running."""
    return {"message": "Hello Scriptdeck"}
