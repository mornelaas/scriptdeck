import sqlite3

with sqlite3.connect("scriptdeck.db") as con:
    cursor = con.cursor()

    cursor.execute("SELECT * FROM scripts")

    scripts = cursor.fetchall()
    for script in scripts:
        print(script)
