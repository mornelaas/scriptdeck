# ScriptDeck

A backend for content creators to manage their scripts through a production lifecycle — from idea to published. Use it from the terminal (CLI) or over HTTP (REST API).

## Tech Stack

- **Python 3.12+**
- **SQLite** — embedded relational database
- **FastAPI** — REST API framework built on type hints
- **Uvicorn** — ASGI server that runs the API
- **Typer** — CLI framework built on type hints
- **Ruff** — linter + formatter
- **uv** — package and environment manager

## The script lifecycle

A script moves through five states:

```
idea → borrador → listo → grabado → publicado
```

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
| GET | `/scripts` | List scripts, optionally filtered by `status` and `creator_id` |
| GET | `/scripts/{script_id}` | Get a single script (404 if it doesn't exist) |
| GET | `/creators` | List all creators |
| GET | `/creators/{creator_id}/scripts` | List a creator's scripts (404 if the creator doesn't exist) |

Example:

```bash
curl "http://127.0.0.1:8000/scripts?status=listo&creator_id=5"
```

## Project structure

```
scriptdeck/
├── src/
│   └── scriptdeck/
│       ├── api.py              # REST API endpoints (FastAPI)
│       ├── cli.py              # CLI commands (Typer)
│       ├── database.py         # Schema and connection factory
│       ├── models.py           # ScriptStatus enum
│       ├── create_scripts.py   # Insert operations
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

Working CLI and a read-only REST API over a normalized SQLite database: full CRUD from the CLI, filtered listing, aggregate statistics, enforced foreign keys and an index on `status`. Type hints across every function and zero Ruff warnings.

Built as a learning project while working through a backend engineering roadmap. Next steps: create, update and delete endpoints with Pydantic validation, migration to PostgreSQL, JWT authentication and a test suite with pytest.