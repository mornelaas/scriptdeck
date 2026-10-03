import sqlite3

from .models import ScriptStatus


def update_status_script(status: str, script_id: int) -> bool:
    with sqlite3.connect("scriptdeck.db") as con:
        cursor = con.cursor()

        cursor.execute(
            "UPDATE scripts SET status = ? WHERE id = ?", (status, script_id)
        )

        return cursor.rowcount > 0


def delete_script(script_id: int) -> bool:
    with sqlite3.connect("scriptdeck.db") as con:
        cursor = con.cursor()
        cursor.execute("DELETE FROM scripts WHERE id = ?", (script_id,))

        return cursor.rowcount > 0


if __name__ == "__main__":
    update_status_script(ScriptStatus.BORRADOR.value, 1)
    delete_script(1)
