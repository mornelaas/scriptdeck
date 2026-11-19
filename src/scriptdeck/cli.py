import typer

from .create_scripts import create_script
from .models import ScriptStatus
from .orm.models import Script
from .orm.session import SessionLocal
from .query import scripts_per_creator, scripts_per_status
from .read_scripts import list_scripts
from .schemas import ScriptUpdate
from .services import InvalidTransitionError, update_script
from .update_delete import delete_script

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
    status: str = "idea",
    platform: str | None = None,
    hook: str | None = None,
    creator_id: int | None = None,
) -> None:
    """Create a script into table scripts"""
    new_id = create_script(
        title=title, status=status, platform=platform, hook=hook, creator_id=creator_id
    )
    print(f"Created script #{new_id}: {title}")


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
    """Delete script from table scripts"""
    was_deleted = delete_script(script_id=script_id)
    if was_deleted:
        print(f"The script {script_id} was deleted")
    else:
        print("None script was deleted")


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
