import sqlite3

from .database import get_connection


def list_scripts(
    status: str | None = None,
    creator_id: int | None = None,
    platform: str | None = None,
) -> list[sqlite3.Row]:
    with get_connection() as con:
        cursor = con.cursor()

        query = "SELECT * FROM scripts"
        conditions = []
        params = []

        if status is not None:
            conditions.append("status = ?")
            params.append(status)

        if creator_id is not None:
            conditions.append("creator_id = ?")
            params.append(creator_id)

        if platform is not None:
            conditions.append("platform = ?")
            params.append(platform)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query, tuple(params))

        return cursor.fetchall()


def get_script(script_id: int) -> sqlite3.Row | None:
    with get_connection() as con:
        cursor = con.cursor()

        cursor.execute("SELECT * FROM scripts WHERE id=?", (script_id,))

        return cursor.fetchone()
