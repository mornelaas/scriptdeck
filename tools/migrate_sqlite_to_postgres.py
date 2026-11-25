"""One-off migration: copy ScriptDeck's data from SQLite into PostgreSQL.

Run it once from the project root, after `alembic upgrade head`:

    uv run python tools/migrate_sqlite_to_postgres.py
"""

from datetime import UTC, datetime

from sqlalchemy import (
    Connection,
    Table,
    create_engine,
    delete,
    func,
    insert,
    select,
    text,
)

from scriptdeck.orm.models import Creator, Script
from scriptdeck.orm.session import engine as postgres_engine

SQLITE_URL = "sqlite:///scriptdeck.db"

sqlite_engine = create_engine(SQLITE_URL)


def copy_rows(source: Connection, target: Connection, table: Table) -> int:
    """Copy every row of a table from SQLite to PostgreSQL, keeping its id."""
    rows = []
    for row in source.execute(select(table)).mappings():
        values = dict(row)
        for column, value in values.items():
            if isinstance(value, datetime):
                values[column] = value.replace(tzinfo=UTC)
        rows.append(values)
    target.execute(insert(table), rows)
    return len(rows)


def main() -> None:
    """Make PostgreSQL a copy of the SQLite data, all or nothing."""
    with sqlite_engine.connect() as source, postgres_engine.begin() as target:
        target.execute(delete(Script.__table__))
        target.execute(delete(Creator.__table__))

        creators = copy_rows(source=source, target=target, table=Creator.__table__)
        scripts = copy_rows(source=source, target=target, table=Script.__table__)

        reset_sequence(target=target, table=Creator.__table__)
        reset_sequence(target=target, table=Script.__table__)

    print(f"Copied {creators} creators and {scripts} scripts")


def reset_sequence(target: Connection, table: Table) -> None:
    """Move the id counter past the copied ids, so new rows don't collide."""
    max_id = target.execute(select(func.max(table.c.id))).scalar_one()
    target.execute(
        text("SELECT setval(pg_get_serial_sequence(:table, 'id'), :max_id)"),
        {"table": table.name, "max_id": max_id},
    )


if __name__ == "__main__":
    main()
