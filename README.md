# ScriptDeck

A backend for content creators to manage their scripts through a production lifecycle — from idea to published. Use it from the terminal (CLI) or over HTTP (REST API).

## Tech Stack

- **Python 3.12+**
- **SQLite** — embedded relational database
- **FastAPI** — REST API framework built on type hints
- **Pydantic** — request and response validation with type hints
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
```

## Usage

### CLI

Once installed, the `scriptdeck` command is available in your terminal.

```bash
# List all scripts
scriptdeck list-all

# Filter by status or creator
scriptdeck list-all --status borrador
scriptdeck list-all --creator-id 3
scriptdeck list-all --status listo --creator-id 3

# Create a script
scriptdeck add "How I started my startup" --platform youtube --status borrador

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
| GET | `/creators` | List all creators |
| POST | `/creators` | Create a creator → 201 (422 if the body is invalid) |
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
│       ├── routers/            # API endpoints, one router per resource
│       │   ├── __init__.py     # Makes routers/ a Python package
│       │   ├── creators.py     # /creators endpoints
│       │   └── scripts.py      # /scripts endpoints
│       ├── cli.py              # CLI commands (Typer)
│       ├── database.py         # Schema and connection factory
│       ├── models.py           # ScriptStatus enum
│       ├── schemas.py          # Pydantic schemas (Create / Update / Out)
│       ├── create_scripts.py   # Insert scripts
│       ├── create_creators.py  # Insert creators
│       ├── read_scripts.py     # Read scripts with filters
│       ├── read_creators.py    # Read creators
│       ├── update_delete.py    # Update and delete operations
│       ├── query.py            # Joins, aggregations, subqueries
│       └── seed.py             # Fake data for development
├── pyproject.toml              # Project metadata, dependencies and tooling config
├── uv.lock                     # Exact versions of every dependency
└── README.md
```

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

Working CLI and REST API over a normalized SQLite database: full CRUD for scripts from both the CLI and the API, filtered listing, aggregate statistics, enforced foreign keys and an index on `status`. The API validates requests and responses with Pydantic schemas and returns proper status codes (201, 204, 404, 409, 422), and status changes follow the script state machine. Type hints across every function and zero Ruff warnings.

Built as a learning project while working through a backend engineering roadmap. Next steps: migration to PostgreSQL, JWT authentication and a test suite with pytest.
