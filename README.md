# JobMatcher AI

AI agent that analyzes a CV against a job posting, calculates a match score, and
suggests CV improvements. Built with Python, Google ADK, Gemini 3.0, Vue 3 and
PostgreSQL.

**Live demo:** _(add URL after deploy)_

---

## Stack

**Backend** (`/backend`)
- Python 3.12
- FastAPI
- Google Agent Development Kit (ADK)
- Gemini 3.0
- SQLAlchemy 2.0 async + asyncpg
- Alembic (migrations)
- Pydantic v2

**Frontend** (`/frontend`)
- Vue 3 + TypeScript
- Pinia (state)
- Vue Router
- TailwindCSS
- Vite

**Infra**
- Docker (multi-stage builds)
- Backend on Google Cloud Run
- Frontend on Vercel
- Database on Neon (PostgreSQL serverless)
- CI/CD via GitHub Actions + Workload Identity Federation
- Secrets in GCP Secret Manager

---

## Local development

Requirements: Docker, Docker Compose.

```bash
cp backend/.env.example backend/.env       # fill in GEMINI_API_KEY
cp frontend/.env.example frontend/.env

# Boots Postgres + backend (with auto-migrations) + frontend
docker compose up

# Backend:  http://localhost:8000
# Frontend: http://localhost:5173
# API docs: http://localhost:8000/docs
# Postgres: localhost:5432  (postgres/postgres, db: jobmatcher)
```

---

## Environment variables

Backend (`backend/.env`):

```
GEMINI_API_KEY=your_key_here
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/jobmatcher
ALLOWED_ORIGINS=http://localhost:5173,https://your-frontend.vercel.app
```

Frontend (`frontend/.env`):

```
VITE_API_URL=http://localhost:8000
```

---

## Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/analyze` | Upload CV (PDF) + job posting → match analysis. Cached by `(cv_hash, job_hash)`. |
| GET  | `/api/stats`   | Total analyses + average match score. |
| GET  | `/health`      | Liveness probe. |
| GET  | `/docs`        | Interactive Swagger UI. |

---

## Project structure

```
job-matcher-agent/
├── backend/                 # FastAPI + Google ADK + Postgres
│   ├── app/
│   │   ├── agents/         # ADK agent definitions
│   │   ├── routes/         # FastAPI endpoints (analyze, stats, health)
│   │   ├── schemas/        # Pydantic models
│   │   ├── services/       # PDF parsing, cache logic
│   │   └── db/             # SQLAlchemy engine, Base, models
│   ├── alembic/            # Migrations
│   ├── tests/
│   ├── Dockerfile          # Prod (runs `alembic upgrade head` then uvicorn)
│   ├── Dockerfile.dev      # Dev with hot reload
│   └── pyproject.toml
├── frontend/                # Vue 3 + TypeScript
│   ├── src/
│   │   ├── api/            # HTTP client
│   │   ├── components/     # UI components
│   │   ├── stores/         # Pinia stores
│   │   ├── types/          # TS types shared with backend schemas
│   │   └── views/          # Page-level components
│   ├── Dockerfile          # Used only if deploying to Cloud Run instead of Vercel
│   └── package.json
├── .github/workflows/
│   ├── deploy-backend.yml  # Cloud Run deploy
│   └── deploy-frontend.yml # Vercel deploy
├── docs/
│   ├── ARCHITECTURE.md
│   └── DEPLOYMENT.md
├── scripts/
│   ├── setup-gcp.sh        # One-time GCP setup (WIF, Artifact Registry, Secrets)
│   └── deploy-backend.sh   # Manual backend deploy
└── docker-compose.yml      # db + backend + frontend
```

See `docs/DEPLOYMENT.md` for the full deploy guide.

---

## License

MIT
