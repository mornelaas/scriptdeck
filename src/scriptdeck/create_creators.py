from .database import get_connection


def create_creator(
    name: str,
    niche: str | None = None,
    handle: str | None = None,
) -> int:
    with get_connection() as con:
        cursor = con.cursor()

        cursor.execute(
            "INSERT INTO creators (name, niche, handle) VALUES (?, ?, ?)",
            (name, niche, handle),
        )

        return cursor.lastrowid
