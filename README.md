# ScriptDeck

A command-line tool for content creators to manage their scripts through a production lifecycle — from idea to published.

## Tech Stack

- **Python 3.12+**
- **SQLite** — embedded relational database
- **Typer** — CLI framework built on type hints
- **Ruff** — linter + formatter
- **uv** — package and environment manager

## The script lifecycle

A script moves through five states:

​```
idea → borrador → listo → grabado → publicado
​```

## Installation

​```bash
# 1. Clone the repository
git clone https://github.com/mornelaas/scriptdeck.git
cd scriptdeck

# 2. Create the virtual environment
uv venv

# 3. Activate it
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

# 4. Install the package and its dependencies
uv pip install -e .
uv pip install -r requirements.txt

# 5. Create the database
python -m scriptdeck.database
​```

## Usage

Once installed, the `scriptdeck` command is available in your terminal.

​```bash
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
​```

Run `scriptdeck --help` to see all commands, or `scriptdeck <command> --help` for details on a specific one.

## Project structure

​```
scriptdeck/
├── src/
│   └── scriptdeck/
│       ├── cli.py              # CLI commands (Typer)
│       ├── database.py         # Schema and connection factory
│       ├── models.py           # ScriptStatus enum
│       ├── create_scripts.py   # Insert operations
│       ├── read_scripts.py     # Read operations with filters
│       ├── update_delete.py    # Update and delete operations
│       ├── query.py            # Joins, aggregations, subqueries
│       └── seed.py             # Fake data for development
├── pyproject.toml              # Project metadata and tooling config
├── requirements.txt            # Dependencies
└── README.md
​```

## Development

​```bash
# Lint and format
ruff check .
ruff format .

# Seed the database with fake data
python -m scriptdeck.seed
​```

## Project status

Fully working CLI over a normalized SQLite database: full CRUD, filtered listing, aggregate statistics, enforced foreign keys and an index on `status`. Type hints across every function and zero Ruff warnings.

Built as a learning project while working through a backend engineering roadmap. Next steps: a REST API with FastAPI, migration to PostgreSQL, JWT authentication and a test suite with pytest.