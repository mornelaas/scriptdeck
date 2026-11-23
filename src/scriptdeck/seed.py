import random

import faker
from sqlalchemy import select
from sqlalchemy.orm import Session

from scriptdeck.models import ScriptStatus
from scriptdeck.orm.models import Creator, Script
from scriptdeck.orm.session import SessionLocal

fake = faker.Faker()

niches = ["finanzas", "fitness", "tech", "gaming", "cocina"]
statuses = list(ScriptStatus)
platforms = ["youtube", "tiktok", "instagram", "linkedin"]


def seed_creators(db: Session) -> None:
    """Add 5 fake creators to the database."""
    for _ in range(5):
        creator = Creator(
            name=fake.name(),
            handle=fake.user_name(),
            niche=random.choice(niches),
        )

        db.add(creator)
    db.commit()


def seed_scripts(db: Session) -> None:
    """Add 15 fake scripts to the database."""
    creator_ids = db.scalars(select(Creator.id)).all()

    for _ in range(15):
        script = Script(
            title=fake.sentence(nb_words=4),
            status=random.choice(statuses),
            platform=random.choice(platforms),
            hook=fake.sentence(nb_words=8),
            creator_id=random.choice(creator_ids),
        )
        db.add(script)
    db.commit()


if __name__ == "__main__":
    with SessionLocal() as db:
        seed_creators(db=db)
        seed_scripts(db=db)
    print("Seeded creators and scripts!")
