from .database import get_connection


def update_status_script(status: str, script_id: int) -> bool:
    with get_connection() as con:
        cursor = con.cursor()

        cursor.execute(
            "UPDATE scripts SET status = ? WHERE id = ?", (status, script_id)
        )

        return cursor.rowcount > 0


def update_script(
    script_id: int,
    title: str,
    status: str,
    platform: str | None,
    hook: str | None,
    notes: str | None,
    creator_id: int | None,
) -> bool:
    with get_connection() as con:
        cursor = con.cursor()

        cursor.execute(
            "UPDATE scripts SET title = ?, status = ?, platform = ?, hook = ?, "
            "notes = ?, creator_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (title, status, platform, hook, notes, creator_id, script_id),
        )

        return cursor.rowcount > 0


def delete_script(script_id: int) -> bool:
    with get_connection() as con:
        cursor = con.cursor()
        cursor.execute("DELETE FROM scripts WHERE id = ?", (script_id,))

        return cursor.rowcount > 0
