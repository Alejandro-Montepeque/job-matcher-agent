# Deployment guide

The project deploys to three platforms:

- **Backend** → Google Cloud Run (via Docker + Artifact Registry).
- **Frontend** → Vercel (static Vue build).
- **Database** → Neon (serverless PostgreSQL).

Both deploys happen automatically on `git push` to `main` (with path filters so each
service redeploys only when its own folder changes).

---

## 0. Set up the database (Neon)

1. Create an account at https://neon.tech (free).
2. Create a project named `jobmatcher-prod`.
3. Copy the connection string. It looks like:
   ```
   postgresql://user:pass@ep-XXXX.us-east-2.aws.neon.tech/jobmatcher?sslmode=require
   ```
4. Replace the driver to use asyncpg:
   ```
   postgresql+asyncpg://user:pass@ep-XXXX.us-east-2.aws.neon.tech/jobmatcher?sslmode=require
   ```

You will paste this into Secret Manager in step 2.

---

## 1. One-time GCP setup

Requires `gcloud` installed and authenticated as a project owner.

```bash
# Create the GCP project (skip if it already exists)
gcloud projects create job-matcher-agent --name="JobMatcher AI"
gcloud config set project job-matcher-agent

# Link a billing account (required even on free tier for Cloud Run)
gcloud beta billing projects link job-matcher-agent --billing-account=XXXXXX-XXXXXX-XXXXXX

# Run the setup script (creates WIF, Service Account, Artifact Registry, Secret Manager)
GITHUB_OWNER=Alejandro-Montepeque GITHUB_REPO=job-matcher-agent \
  bash scripts/setup-gcp.sh
```

The script prints 4 values at the end. Save them.

## 2. Configure GitHub secrets (backend)

In `github.com/Alejandro-Montepeque/job-matcher-agent/settings/secrets/actions`, add:

| Secret | Value |
|---|---|
| `GCP_PROJECT_ID` | `job-matcher-agent` |
| `GCP_SERVICE_ACCOUNT` | `github-actions@job-matcher-agent.iam.gserviceaccount.com` |
| `GCP_WIF_PROVIDER` | `projects/NUMBER/locations/global/workloadIdentityPools/github-actions-pool/providers/github-actions-provider` |
| `ALLOWED_ORIGINS` | `https://your-frontend.vercel.app` (set after first Vercel deploy) |

Then set the real Gemini API key and Neon URL in Secret Manager:

```bash
echo -n "YOUR_GEMINI_KEY" | \
  gcloud secrets versions add gemini-api-key --data-file=- --project=job-matcher-agent

echo -n "postgresql+asyncpg://user:pass@ep-XXXX.neon.tech/jobmatcher?sslmode=require" | \
  gcloud secrets versions add database-url --data-file=- --project=job-matcher-agent
```

The container runs `alembic upgrade head` on startup, so the schema is applied
automatically on the first deploy.

## 3. Configure Vercel (frontend)

```bash
cd frontend
npm i -g vercel
vercel login
vercel link        # creates .vercel/project.json with org/project IDs
```

Then in Vercel project settings → Environment Variables:

| Variable | Value |
|---|---|
| `VITE_API_URL` | `https://job-matcher-api-XXXX-uc.a.run.app` (Cloud Run URL after backend deploy) |

## 4. Configure GitHub secrets (frontend)

| Secret | Value |
|---|---|
| `VERCEL_TOKEN` | Generate at https://vercel.com/account/tokens |
| `VERCEL_ORG_ID` | From `frontend/.vercel/project.json` (`orgId`) |
| `VERCEL_PROJECT_ID` | From `frontend/.vercel/project.json` (`projectId`) |

## 5. First deploy

```bash
git add .
git commit -m "feat: initial scaffold"
git push origin main
```

Both workflows run in parallel:
- `deploy-backend.yml` → builds Docker, pushes to Artifact Registry, deploys Cloud Run.
- `deploy-frontend.yml` → builds Vue, deploys to Vercel.

After both finish, grab the Cloud Run URL and update `VITE_API_URL` in Vercel, then
redeploy frontend (or push any change to `frontend/`).

---

## Manual deploys (optional)

If you want to redeploy backend without pushing to GitHub:

```bash
PROJECT_ID=job-matcher-agent bash scripts/deploy-backend.sh
```

For frontend:

```bash
cd frontend
vercel --prod
```

---

## Rollback

Cloud Run keeps every revision. To roll back:

```bash
gcloud run services update-traffic job-matcher-api \
  --to-revisions=PREVIOUS_REVISION=100 \
  --region=us-central1 --project=job-matcher-agent
```

Vercel keeps every deployment. In the dashboard, click any previous deployment and
"Promote to Production".

---

## Cost expectations

**Cloud Run (backend)**

- Free tier: 2M requests, 360k vCPU-seconds, 180k GiB-seconds memory per month.
- A demo with < 1000 analyses/month will stay free.
- Each Gemini call: ~$0.0001–$0.001 depending on input length. Free tier covers ~1500
  requests/day on Gemini 2.0 Flash.

**Vercel (frontend)**

- Free Hobby tier: 100 GB bandwidth/month, unlimited deploys.
- Static Vue app weighs < 200 KB gzipped. Effectively free.

**Neon (database)**

- Free tier: 0.5 GB storage, 191 compute hours/month (scale-to-zero after 5 min idle).
- For a portfolio demo with < 10k analyses, free is enough.
- Connection pooling via Neon's pooler endpoint if needed.
