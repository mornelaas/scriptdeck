import sqlite3

con = sqlite3.connect("scriptdeck.db")

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
con.commit()
con.close()
