from .database import get_connection


def create_script(
    title: str,
    status: str = "idea",
    platform: str | None = None,
    hook: str | None = None,
    notes: str | None = None,
    creator_id: int | None = None,
) -> int:
    with get_connection() as con:
        cursor = con.cursor()

        cursor.execute(
            "INSERT INTO scripts (title, status, platform, hook, notes, creator_id) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (title, status, platform, hook, notes, creator_id),
        )

        return cursor.lastrowid
