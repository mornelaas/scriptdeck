import typer

from .create_scripts import create_script
from .query import scripts_per_creator, scripts_per_status
from .read_scripts import list_scripts
from .update_delete import delete_script, update_status_script

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
def update(script_id: int, status: str) -> None:
    """Update a script status into table scripts"""
    was_updated = update_status_script(status=status, script_id=script_id)
    if was_updated:
        print(f"The script {script_id} change status to: {status}")
    else:
        print("None script was updated")


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
