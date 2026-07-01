import sqlite3


def init_db() -> None:
    with sqlite3.connect("scriptdeck.db") as con:
        cursor = con.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'idea' CHECK (status IN ('idea', 'borrador', 'listo', 'grabado', 'publicado')),
                platform TEXT,
                hook TEXT,
                notes TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS creators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            niche TEXT,
            handle TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )


if __name__ == "__main__":
    init_db()
