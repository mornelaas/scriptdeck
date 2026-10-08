from scriptdeck.models import ScriptStatus

from .database import get_connection


def list_creators() -> list[tuple]:
    with get_connection() as con:
        cursor = con.cursor()
        cursor.execute("SELECT name, niche FROM creators")
        return cursor.fetchall()


def scripts_with_creators() -> list[tuple]:
    with get_connection() as con:
        cursor = con.cursor()
        cursor.execute(
            "SELECT scripts.title, creators.name "
            "FROM scripts INNER JOIN creators "
            "ON scripts.creator_id = creators.id"
        )
        return cursor.fetchall()


def scripts_per_creator() -> list[tuple]:
    with get_connection() as con:
        cursor = con.cursor()
        cursor.execute("SELECT creator_id, COUNT(*) FROM scripts GROUP BY creator_id")
        return cursor.fetchall()


def scripts_per_status() -> list[tuple]:
    with get_connection() as con:
        cursor = con.cursor()
        cursor.execute("SELECT status, COUNT(*) FROM scripts GROUP BY status")
        return cursor.fetchall()


def all_scripts_with_creators() -> list[tuple]:
    with get_connection() as con:
        cursor = con.cursor()
        cursor.execute(
            "SELECT scripts.title, creators.name "
            "FROM scripts LEFT JOIN creators "
            "ON scripts.creator_id = creators.id"
        )
        return cursor.fetchall()


def all_creators_with_scripts() -> list[tuple]:
    with get_connection() as con:
        cursor = con.cursor()
        cursor.execute(
            "SELECT creators.name, scripts.title "
            "FROM creators LEFT JOIN scripts "
            "ON creators.id = scripts.creator_id"
        )
        return cursor.fetchall()


def scripts_per_creator_by_status(status_script: str) -> list[tuple]:
    with get_connection() as con:
        cursor = con.cursor()
        cursor.execute(
            "SELECT creators.name, COUNT(*) FROM scripts "
            "INNER JOIN creators "
            "ON scripts.creator_id = creators.id "
            "WHERE status = ? GROUP BY creators.name",
            (status_script,),
        )
        return cursor.fetchall()


def scripts_by_creator_niche(niche: str) -> list[tuple]:
    with get_connection() as con:
        cursor = con.cursor()
        cursor.execute(
            "SELECT title FROM scripts "
            "WHERE creator_id IN (SELECT id FROM creators WHERE niche = ?)",
            (niche,),
        )
        return cursor.fetchall()


def creators_with_script_count() -> list[tuple]:
    with get_connection() as con:
        cursor = con.cursor()
        cursor.execute(
            "SELECT name, (SELECT COUNT(*) FROM scripts "
            "WHERE scripts.creator_id = creators.id) AS total "
            "FROM creators"
        )
        return cursor.fetchall()


if __name__ == "__main__":
    print("Creators and niches", list_creators())
    print("Creators with their scripts", scripts_with_creators())
    print("Number of scripts per creator", scripts_per_creator())
    print("Number of scripts per status", scripts_per_status())
    print("All the scripts with their creator", all_scripts_with_creators())
    print("All creators with their scripts", all_creators_with_scripts())
    print(
        "All published scripts per creator",
        scripts_per_creator_by_status(ScriptStatus.PUBLICADO.value),
    )
