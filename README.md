# ScriptDeck

A backend for content creators to manage their scripts through a production lifecycle — from idea to published. Use it from the terminal (CLI) or over HTTP (REST API).

## Tech Stack

- **Python 3.12+**
- **SQLite** — embedded relational database
- **SQLAlchemy** — ORM that maps the tables to Python classes
- **FastAPI** — REST API framework built on type hints
- **Pydantic** — request and response validation with type hints
- **pydantic-settings** — configuration from environment variables and `.env`
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

# 4. Create the database
python -m scriptdeck.database

# 5. Create your local configuration from the template
cp .env.example .env
```

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

Business rules:

- Every new script starts in `idea`: the create body has no `status`.
- `PUT` replaces a script's content but keeps its `status`.
- Status changes go through `PATCH`, one step at a time; any other move returns 409.

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
│       │   ├── creators.py     # /creators endpoints
│       │   └── scripts.py      # /scripts endpoints
│       ├── dependencies.py     # Shared FastAPI dependencies (SessionDep, ScriptDep, CreatorDep)
│       ├── services.py         # Script operations shared by the API and the CLI (service layer)
│       ├── orm/                # SQLAlchemy ORM: engine, sessions and models
│       │   ├── __init__.py     # Makes orm/ a Python package
│       │   ├── models.py       # Script and Creator mapped to the existing tables
│       │   └── session.py      # Engine, session factory and get_db
│       ├── cli.py              # CLI commands (Typer)
│       ├── database.py         # Creates the SQLite tables (init_db); Alembic migrations will replace it
│       ├── models.py           # ScriptStatus enum
│       ├── schemas.py          # Pydantic schemas (Create / Update / Out)
│       └── seed.py             # Fake data for development, written through the ORM
├── .env.example                # Template for your local .env (copy it and fill it in)
├── pyproject.toml              # Project metadata, dependencies and tooling config
├── uv.lock                     # Exact versions of every dependency
└── README.md
```

## Architecture

The API and the CLI are two entry points to the same service layer. The script operations live in `services.py`, and both call them instead of repeating the logic:

```
HTTP request → router ─┐
                       ├→ services.py → ORM session → SQLite
CLI command  → cli.py ─┘
```

- `services.py` holds the script rules: the creator must exist, and status changes follow the state machine.
- It raises domain errors (`CreatorNotFoundError`, `InvalidTransitionError`), and each entry point translates them: the API into HTTP status codes (422, 409), the CLI into a message and exit code 1.
- The API gets its session from `SessionDep`, which opens one session per request (`get_db`) and always closes it. The CLI opens its own with `with SessionLocal() as db:`.
- `ScriptDep` and `CreatorDep` load the resource from the path or stop the request with a 404 (`get_script_or_404`, `get_creator_or_404`).
- The `/creators` endpoints are simpler and still use the ORM session directly from their router.
- Writes follow the session cycle: `add` → `commit` → `refresh`.
- SQLite foreign keys are enforced on every ORM connection (`PRAGMA foreign_keys=ON`).
- `created_at`, `updated_at` and `status` are filled by the database; `updated_at` changes on every update.

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

## Project status

Working CLI and REST API over a normalized SQLite database: full CRUD for scripts from both the CLI and the API, filtered listing, aggregate statistics, enforced foreign keys and an index on `status`. The API validates requests and responses with Pydantic schemas and returns proper status codes (201, 204, 404, 409, 422), and status changes follow the script state machine. Type hints across every function and zero Ruff warnings. The API is organized in routers (one per resource). The API and the CLI share a service layer for script operations, and both talk to the database through the SQLAlchemy ORM. Configuration (the database URL) is read from environment variables and a local `.env` file with pydantic-settings.

Built as a learning project while working through a backend engineering roadmap. Next steps: migration to PostgreSQL with Alembic, JWT authentication and a test suite with pytest.
