import typer
from pydantic import ValidationError

from .models import ScriptStatus
from .orm.models import Script
from .orm.session import SessionLocal
from .query import scripts_per_creator, scripts_per_status
from .read_scripts import list_scripts
from .schemas import ScriptCreate, ScriptUpdate
from .services import (
    CreatorNotFoundError,
    InvalidTransitionError,
    create_script,
    delete_script,
    update_script,
)

app = typer.Typer()


@app.command()
def list_all(creator_id: int | None = None, status: str | None = None) -> None:
    """List all scripts in the database."""
    scripts = list_scripts(creator_id=creator_id, status=status)
    for script in scripts:
        print(
            f"#{script[0]} title: {script[1]} status: {script[2]} platform: {script[3]}"
        )


@app.command()
def add(
    title: str,
    platform: str | None = None,
    hook: str | None = None,
    creator_id: int | None = None,
) -> None:
    """Create a new script. It always starts in the 'idea' status."""
    try:
        data = ScriptCreate(
            title=title, platform=platform, hook=hook, creator_id=creator_id
        )
    except ValidationError as error:
        print(error)
        raise typer.Exit(code=1) from error

    with SessionLocal() as db:
        try:
            script = create_script(db=db, data=data)
        except CreatorNotFoundError as error:
            print(error)
            raise typer.Exit(code=1) from error

        print(f"Created script #{script.id}: {script.title}")


@app.command()
def update(script_id: int, status: ScriptStatus) -> None:
    """Change the status of a script, following the state machine."""
    with SessionLocal() as db:
        script = db.get(Script, script_id)
        if script is None:
            print(f"Script #{script_id} not found")
            raise typer.Exit(code=1)

        try:
            update_script(db, script, ScriptUpdate(status=status))
        except InvalidTransitionError as error:
            print(error)
            raise typer.Exit(code=1) from error

        print(f"Script #{script_id} moved to: {status.value}")


@app.command()
def delete(script_id: int) -> None:
    """Delete a script for good."""
    with SessionLocal() as db:
        script = db.get(Script, script_id)
        if script is None:
            print(f"Script #{script_id} not found")
            raise typer.Exit(code=1)

        delete_script(db, script)
        print(f"Script #{script_id} deleted")


@app.command()
def stats() -> None:
    """Stats of: Scripts by status and Scripts by creator"""
    stat_scripts_per_status = scripts_per_status()
    stat_scripts_per_creator = scripts_per_creator()

    print("Scripts by status:")
    for status, count in stat_scripts_per_status:
        print(f"  {status}: {count}")

    print("Scripts by creator:")
    for creator, count in stat_scripts_per_creator:
        print(f"  {creator}: {count}")


if __name__ == "__main__":
    app()
