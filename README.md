# ScriptDeck

A backend for content creators to manage their scripts through a production lifecycle — from idea to published. Use it from the terminal (CLI) or over HTTP (REST API).

## Tech Stack

- **Python 3.12+**
- **PostgreSQL 18** — relational database server
- **SQLAlchemy** — ORM that maps the tables to Python classes
- **psycopg 3** — PostgreSQL driver that SQLAlchemy uses under the hood
- **Alembic** — versioned database migrations generated from the models
- **FastAPI** — REST API framework built on type hints
- **Pydantic** — request and response validation with type hints
- **email-validator** — email format checks for Pydantic's `EmailStr`
- **pydantic-settings** — configuration from environment variables and `.env`
- **pwdlib + Argon2id** — password hashing
- **Uvicorn** — ASGI server that runs the API
- **Typer** — CLI framework built on type hints
- **Ruff** — linter + formatter
- **uv** — package and environment manager

## The script lifecycle

A script moves through five states:

```
idea → borrador → listo → grabado → publicado
```

A script moves one step at a time, forward or back. `publicado` is final: once published, its status can't change.

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/mornelaas/scriptdeck.git
cd scriptdeck

# 2. Create the virtual environment and install dependencies
uv sync

# 3. Activate it
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

# 4. Create your local configuration from the template
cp .env.example .env
```

### Database

ScriptDeck needs a running PostgreSQL 18 server. On macOS, [Postgres.app](https://postgresapp.com/) is the easiest way to get one.

Create a role for the app and a database it owns. In `psql`, connected as your superuser:

```sql
CREATE ROLE scriptdeck_app WITH LOGIN;
\password scriptdeck_app
CREATE DATABASE scriptdeck OWNER scriptdeck_app;
```

Put that password in `DATABASE_URL` in your `.env` (letters and numbers only, so the URL stays valid). Then create the tables:

```bash
alembic upgrade head
```

The app connects with its own role instead of a superuser (least privilege): if its credentials ever leak, they only reach the `scriptdeck` database.

## Usage

### CLI

Once installed, the `scriptdeck` command is available in your terminal.

```bash
# List all scripts
scriptdeck list-all

# Filter by status, creator or platform
scriptdeck list-all --status borrador
scriptdeck list-all --creator-id 3
scriptdeck list-all --platform tiktok
scriptdeck list-all --status listo --creator-id 3

# Create a script (it always starts in idea)
scriptdeck add "How I started my startup" --platform youtube

# Update a script's status
scriptdeck update 7 grabado

# Delete a script
scriptdeck delete 7

# Show statistics
scriptdeck stats
```

Run `scriptdeck --help` to see all commands, or `scriptdeck <command> --help` for details on a specific one.

### REST API

Start the development server:

```bash
uv run uvicorn scriptdeck.api:app --reload
```

The API runs at http://127.0.0.1:8000. Interactive docs:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |
| GET | `/scripts` | List scripts, optionally filtered by `status`, `creator_id` and `platform` |
| GET | `/scripts/{script_id}` | Get a single script (404 if it doesn't exist) |
| POST | `/scripts` | Create a script → 201 (422 if the body is invalid or the creator doesn't exist) |
| PUT | `/scripts/{script_id}` | Replace a script's content → 200 (404 / 422) |
| PATCH | `/scripts/{script_id}` | Update only the fields sent → 200 (404 / 409 / 422) |
| DELETE | `/scripts/{script_id}` | Delete a script → 204 (404 if it doesn't exist) |
| GET | `/creators` | List creators, optionally filtered by `niche` |
| POST | `/creators` | Create a creator → 201 (422 if the body is invalid) |
| PATCH | `/creators/{creator_id}` | Update only the fields sent → 200 (404 / 422 if the handle doesn't start with @) |
| GET | `/creators/{creator_id}/scripts` | List a creator's scripts (404 if the creator doesn't exist) |
| POST | `/auth/register` | Register a user → 201 (409 if the email is already registered, 422 if the email is invalid or the password is shorter than 15 characters) |

Business rules:

- Every new script starts in `idea`: the create body has no `status`.
- `PUT` replaces a script's content but keeps its `status`.
- Status changes go through `PATCH`, one step at a time; any other move returns 409.
- Emails are stored in lowercase, so `Orne@Example.com` and `orne@example.com` are the same account.
- Passwords must be 15 to 128 characters long, following NIST SP 800-63B for password-only logins.
- Passwords are never stored: only their Argon2id hash, with a random salt per user. Responses never include the password or its hash.

Example:

```bash
curl -X POST http://127.0.0.1:8000/scripts \
  -H "Content-Type: application/json" \
  -d '{"title": "How I started my startup", "platform": "youtube"}'
```

## Project structure

```
scriptdeck/
├── src/
│   └── scriptdeck/
│       ├── api.py              # FastAPI app entry point (includes the routers)
│       ├── config.py           # Settings read from environment variables and .env
│       ├── routers/            # API endpoints, one router per resource
│       │   ├── __init__.py     # Makes routers/ a Python package
│       │   ├── auth.py         # /auth endpoints (registration)
│       │   ├── creators.py     # /creators endpoints
│       │   └── scripts.py      # /scripts endpoints
│       ├── dependencies.py     # Shared FastAPI dependencies (SessionDep, ScriptDep, CreatorDep)
│       ├── services.py         # Script and user operations shared by the API and the CLI (service layer)
│       ├── security.py         # Password hashing and verification with Argon2id (pwdlib)
│       ├── orm/                # SQLAlchemy ORM: engine, sessions and models
│       │   ├── __init__.py     # Makes orm/ a Python package
│       │   ├── models.py       # Script, Creator and User models: the source of truth for the schema
│       │   └── session.py      # Engine, session factory and get_db
│       ├── cli.py              # CLI commands (Typer)
│       ├── models.py           # ScriptStatus enum
│       ├── schemas.py          # Pydantic schemas (Create / Update / Out)
│       └── seed.py             # Fake data for development, written through the ORM
├── migrations/                 # Alembic migration environment
│   ├── env.py                  # Connects Alembic to DATABASE_URL and the ORM models
│   └── versions/               # One file per schema change, each with upgrade and downgrade
├── tools/
│   └── migrate_sqlite_to_postgres.py  # One-off copy of the old SQLite data into PostgreSQL
├── alembic.ini                 # Alembic configuration (no database URL: it comes from .env)
├── .env.example                # Template for your local .env (copy it and fill it in)
├── pyproject.toml              # Project metadata, dependencies and tooling config
├── uv.lock                     # Exact versions of every dependency
└── README.md
```

## Architecture

The API and the CLI are two entry points to the same service layer. The script operations live in `services.py`, and both call them instead of repeating the logic:

```
HTTP request → router ─┐
                       ├→ services.py → ORM session → PostgreSQL
CLI command  → cli.py ─┘
```

- `services.py` holds the script rules: the creator must exist, and status changes follow the state machine.
- It raises domain errors (`CreatorNotFoundError`, `InvalidTransitionError`), and each entry point translates them: the API into HTTP status codes (422, 409), the CLI into a message and exit code 1.
- Registration follows the same pattern: `register_user` lowercases the email, raises `EmailAlreadyRegisteredError` if it is taken (the API returns 409), and stores only the password hash. Hashing lives in `security.py`, so the rest of the app never touches the hashing library.
- The API gets its session from `SessionDep`, which opens one session per request (`get_db`) and always closes it. The CLI opens its own with `with SessionLocal() as db:`.
- `ScriptDep` and `CreatorDep` load the resource from the path or stop the request with a 404 (`get_script_or_404`, `get_creator_or_404`).
- The `/creators` endpoints are simpler and still use the ORM session directly from their router.
- Writes follow the session cycle: `add` → `commit` → `refresh`.
- The ORM models are the source of truth for the schema. Alembic turns every change into a versioned migration in `migrations/versions/`.
- `created_at` and `updated_at` are `timestamptz`: each one stores an exact instant, in UTC.
- `status` is a native PostgreSQL ENUM (`scriptstatus`), so `ORDER BY status` follows the lifecycle, from `idea` to `publicado`.
- Deleting a creator deletes their scripts: `ON DELETE CASCADE` in the database, plus `cascade="all, delete"` and `passive_deletes=True` on the relationship, so the ORM leaves the cascade to PostgreSQL.
- `scripts.status` and `scripts.creator_id` are indexed, and every constraint follows a naming convention (`pk_scripts`, `fk_scripts_creator_id_creators`), so migrations can refer to them by name.
- `users.email` has a unique constraint (`uq_users_email`), backed by its own index: the database rejects a duplicate email even if two requests arrive at the same time.
- `created_at`, `updated_at` and `status` get their defaults from the database; SQLAlchemy refreshes `updated_at` on every ORM update.

## Development

```bash
# Lint and format
ruff check .
ruff format .

# Install pre-commit hooks (runs Ruff automatically before each commit)
pre-commit install

# Seed the database with fake data
python -m scriptdeck.seed
```

### Database migrations

```bash
# After changing the models: generate a migration, then review it line by line
alembic revision --autogenerate -m "describe the change"

# Apply every pending migration
alembic upgrade head

# Undo the last migration
alembic downgrade -1

# Show which revision the database is at
alembic current
```

Autogenerate writes a draft, so always review it before applying it. For example, it does not drop PostgreSQL ENUM types in `downgrade`.

## Project status

Working CLI and REST API over PostgreSQL, with the schema versioned by Alembic migrations: full CRUD for scripts from both the CLI and the API, filtered listing, aggregate statistics, foreign keys with `ON DELETE CASCADE`, and indexes on `status` and `creator_id`. The data from the original SQLite version was copied with a one-off script and checked row by row. The API validates requests and responses with Pydantic schemas and returns proper status codes (201, 204, 404, 409, 422), and status changes follow the script state machine. Type hints across every function and zero Ruff warnings. The API is organized in routers (one per resource). The API and the CLI share a service layer for script operations, and both talk to the database through the SQLAlchemy ORM. Configuration (the database URL) is read from environment variables and a local `.env` file with pydantic-settings. Users can register: emails are unique and stored in lowercase, and passwords are stored only as Argon2id hashes.

Built as a learning project while working through a backend engineering roadmap. Next steps: JWT login and protected routes, a test suite with pytest and a public deployment.
