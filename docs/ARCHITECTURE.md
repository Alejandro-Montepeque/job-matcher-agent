# Architecture

```
┌──────────────────────┐         ┌──────────────────────┐
│  Vue 3 + Vite        │  HTTPS  │  FastAPI (Python)    │
│  (Vercel CDN)        │ ──────► │  (Google Cloud Run)  │
│                      │         │                       │
│  - File upload       │         │  - /api/analyze       │
│  - Job posting input │         │  - /api/stats         │
│  - Pinia state       │         │  - PDF text extract   │
│                      │         │  - Match agent (ADK)  │
│                      │ ◄────── │                       │
└──────────────────────┘  JSON   └─────┬────────────┬───┘
                                       │            │
                                       │            │ google-generativeai
                          asyncpg/SSL  │            ▼
                                       │   ┌──────────────────────┐
                                       │   │  Gemini 2.0 Flash    │
                                       │   │  (Google AI API)     │
                                       │   └──────────────────────┘
                                       ▼
                            ┌────────────────────────┐
                            │  PostgreSQL (Neon)     │
                            │  - analyses table      │
                            │  - cache lookup        │
                            │  - stats aggregation   │
                            └────────────────────────┘
```

## Components

| Layer | Tech | Hosted on |
|---|---|---|
| Frontend | Vue 3 + TS + Pinia + Tailwind | Vercel (CDN) |
| Backend | FastAPI + Google ADK + Gemini | Google Cloud Run |
| Database | PostgreSQL 16 | Neon (serverless, scale-to-zero) |
| ORM | SQLAlchemy 2.0 async + asyncpg | — |
| Migrations | Alembic | runs on container startup |
| Secrets | GCP Secret Manager | mounted as env vars in Cloud Run |
| CI/CD | GitHub Actions + Workload Identity | — |
| Image registry | Artifact Registry | us-central1 |

## Data model

Single table `analyses`:

| Column | Type | Notes |
|---|---|---|
| id | uuid | PK |
| created_at | timestamptz | indexed, default now() |
| cv_hash | char(64) | SHA-256 of PDF bytes, indexed |
| cv_filename | varchar(255) | original filename |
| job_hash | char(64) | SHA-256 of trimmed job posting, indexed |
| job_posting | text | raw job posting |
| match_score | int | 0-100 |
| summary | text | one-paragraph assessment |
| matches | jsonb | array of strings |
| gaps | jsonb | array of strings |
| suggestions | jsonb | array of `{title, detail}` |

`UNIQUE (cv_hash, job_hash)` for idempotent cache.

## Data flow

1. User uploads CV (PDF) + pastes job posting in Vue form.
2. Frontend `POST /api/analyze` with `multipart/form-data`.
3. Backend computes `cv_hash = sha256(pdf_bytes)` and `job_hash = sha256(job_posting)`.
4. **Cache lookup**: query `analyses` for `(cv_hash, job_hash)`.
   - Hit → return cached row with `cached: true`. No Gemini call.
   - Miss → continue.
5. Extract text from PDF with `pypdf`.
6. Call Gemini via `google-generativeai` with `response_mime_type=application/json`.
7. Validate with Pydantic, insert into `analyses`, return response.

## Why each choice

**Why Postgres (not Firestore or no DB):**
- Real SQL skills visible on portfolio (modeling, indexes, unique constraints).
- Cache by `(cv_hash, job_hash)` is a perfect fit for a relational unique constraint.
- Aggregate queries for `/api/stats` are trivial in SQL.

**Why Neon (not Cloud SQL):**
- Serverless, scales to zero (Cloud SQL has a minimum ~$7/month even idle).
- Free tier covers a portfolio demo comfortably.
- Adds a different cloud vendor to the stack (more breadth for recruiters).

**Why SQLAlchemy async (not Django ORM, not raw asyncpg):**
- Industry standard for non-Django Python.
- Async fits FastAPI's concurrency model.
- Alembic gives versioned migrations (no `db.create_all()` in production).

**Why a single table:**
- The domain has one entity. Adding `users`, `sessions`, etc. without need would be
  overengineering for a portfolio demo.

## Trade-offs

- **No auth**: public endpoint. With Neon + Supabase auth or Firebase Auth this is
  a small addition for v2.
- **No PDF storage**: only the hash and filename are kept. PDFs are not retrievable.
  Storing them would require a Storage bucket (GCS or Supabase Storage).
- **Cache never invalidates**: if the agent's prompt changes, old results stay cached.
  Versioning the cache key with a `prompt_version` would fix it.

## Future improvements

- Stream the response (`StreamingResponse` + Server-Sent Events).
- OCR fallback (`tesseract`) for scanned PDFs.
- Rate limiting (`slowapi`).
- Per-user history (Supabase Auth + extra table).
- Redis in front of Postgres for sub-millisecond cache lookups.
