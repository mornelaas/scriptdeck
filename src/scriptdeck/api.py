from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root() -> dict[str, str]:
    """Check that the ScriptDeck API is running."""
    return {"message": "Hello Scriptdeck"}
