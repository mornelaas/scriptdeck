import sqlite3

with sqlite3.connect("scriptdeck.db") as con:
    cursor = con.cursor()

    cursor.execute(
        "SELECT name, niche FROM creators"
    )
    results = cursor.fetchall()
    print("Creators and niches:", results)

    cursor.execute(
        "SELECT scripts.title, creators.name FROM scripts INNER JOIN creators ON scripts.creator_id = creators.id"
    )
    results = cursor.fetchall()
    print("Scripts with their creator (INNER JOIN):", results)

    cursor.execute(
        "SELECT creator_id, COUNT(*) FROM scripts GROUP BY creator_id"
    )
    results = cursor.fetchall()
    print("Scripts per creator:", results)

    cursor.execute(
        "SELECT status, COUNT(*) FROM scripts GROUP BY status"
    )
    results = cursor.fetchall()
    print("Scripts per status:", results)

    cursor.execute(
        "SELECT scripts.title, creators.name FROM scripts LEFT JOIN creators ON scripts.creator_id = creators.id"
    )
    results = cursor.fetchall()
    print("All scripts, with or without creator (LEFT JOIN):", results)

    cursor.execute(
        "SELECT creators.name, scripts.title FROM creators LEFT JOIN scripts ON creators.id = scripts.creator_id"
    )
    results = cursor.fetchall()
    print("All creators, with or without scripts (LEFT JOIN):", results)

    cursor.execute(
        "SELECT creators.name, COUNT(*) FROM scripts INNER JOIN creators ON scripts.creator_id = creators.id WHERE status = 'publicado' GROUP BY creators.name"
    )
    results = cursor.fetchall()
    print("Published scripts per creator:", results)
