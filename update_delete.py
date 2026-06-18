import sqlite3

with sqlite3.connect("scriptdeck.db") as con:
    cursor = con.cursor()

    cursor.execute("UPDATE scripts SET status = ? WHERE id = ?",
                   ("borrador", 1))

    cursor.execute("DELETE FROM scripts WHERE id = ?", (999,))
