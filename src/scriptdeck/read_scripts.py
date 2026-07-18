import sqlite3


def list_scripts() -> None:
    with sqlite3.connect("scriptdeck.db") as con:
        cursor = con.cursor()

        cursor.execute("SELECT * FROM scripts")

        scripts = cursor.fetchall()
        for script in scripts:
            print(script)


if __name__ == "__main__":
    list_scripts()
