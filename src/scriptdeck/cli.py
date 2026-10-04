import typer

from .read_scripts import list_scripts
from .create_scripts import create_script

app = typer.Typer()


@app.command()
def list_all() -> None:
    """List all scripts in the database."""
    scripts = list_scripts()
    for script in scripts:
        print(script)

@app.command()
def add(
    title: str,
    status: str = "idea",
    platform: str | None = None,
    hook: str | None = None,
    creator_id: int | None = None,
) -> None:
    """Create a script into table scripts"""
    new_id = create_script(title= title, status= status, platform= platform, hook= hook, creator_id= creator_id)
    print(f"Created script #{new_id}: {title}")

if __name__ == "__main__":
    app()
