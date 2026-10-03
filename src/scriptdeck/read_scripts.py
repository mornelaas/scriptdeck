import sqlite3


def list_scripts() -> list[tuple]:
    with sqlite3.connect("scriptdeck.db") as con:
        cursor = con.cursor()

        cursor.execute("SELECT * FROM scripts")

        return cursor.fetchall()


if __name__ == "__main__":
    list_scripts()
