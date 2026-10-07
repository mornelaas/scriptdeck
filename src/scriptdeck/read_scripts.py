from .database import get_connection


def list_scripts(
    status: str | None = None, creator_id: int | None = None
) -> list[tuple]:
    with get_connection() as con:
        cursor = con.cursor()

        query = "SELECT * FROM scripts"
        conditions = []
        params = []

        if status is not None:
            conditions.append("status = ?")
            params.append(status)

        if creator_id is not None:
            conditions.append("creator_id = ?")
            params.append(creator_id)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query, tuple(params))

        return cursor.fetchall()


if __name__ == "__main__":
    list_scripts()
