import sqlite3

from .database import get_connection


def list_creators() -> list[sqlite3.Row]:
    with get_connection() as con:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM creators")

        return cursor.fetchall()


def get_creator(creator_id: int) -> sqlite3.Row | None:
    with get_connection() as con:
        cursor = con.cursor()

        cursor.execute("SELECT * FROM creators WHERE id=?", (creator_id,))

        return cursor.fetchone()
