# Backend — JobMatcher API

FastAPI service with the Google ADK + Gemini agent.

## Run locally (without Docker)

```bash
cp .env.example .env
# fill in GEMINI_API_KEY and a DATABASE_URL pointing to a running Postgres
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

API at http://localhost:8000, docs at http://localhost:8000/docs.

## Run with Docker (recommended)

From the repo root:

```bash
docker compose up
```

This boots Postgres + backend (with auto-migrations) + frontend.

## Migrations

```bash
# Create a new migration after editing app/db/models.py
alembic revision --autogenerate -m "describe change"

# Apply pending migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1
```

## Test

```bash
pytest
```

## Lint

```bash
ruff check .
ruff format .
```
