from .database import get_connection


def list_scripts() -> list[tuple]:
    with get_connection() as con:
        cursor = con.cursor()

        cursor.execute("SELECT * FROM scripts")

        return cursor.fetchall()


if __name__ == "__main__":
    list_scripts()
