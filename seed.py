import faker
import random
import sqlite3

fake = faker.Faker()

niches = ["finanzas", "fitness", "tech", "gaming", "cocina"]
statuses = ["idea", "borrador", "listo", "grabado", "publicado"]
platforms = ["youtube", "tiktok", "instagram", "linkedin"]

with sqlite3.connect("scriptdeck.db") as con:
    cursor = con.cursor()

    for _ in range(5):
        name = fake.name()
        handle = fake.user_name()
        niche = random.choice(niches)
        cursor.execute(
            "INSERT INTO creators (name, niche, handle) VALUES (?, ?, ?)",
            (name, niche, handle)
        )

    cursor.execute("SELECT id FROM creators")
    creator_ids = [row[0] for row in cursor.fetchall()]

    for _ in range(15):
        title = fake.sentence(nb_words=4)
        status = random.choice(statuses)
        platform = random.choice(platforms)
        hook = fake.sentence(nb_words=8)
        creator_id = random.choice(creator_ids)
        cursor.execute(
            "INSERT INTO scripts (title, status, platform, hook, creator_id) VALUES (?, ?, ?, ?, ?)",
            (title, status, platform, hook, creator_id)
        )

print("Seeded creators and scripts!")
