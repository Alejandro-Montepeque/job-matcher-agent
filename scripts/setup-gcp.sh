#!/usr/bin/env bash
# One-time setup for GCP: Workload Identity Federation + Artifact Registry + Secret Manager.
# Run once after creating the GCP project. Requires gcloud authenticated as project owner.

set -euo pipefail

PROJECT_ID="${PROJECT_ID:-job-matcher-agent}"
REGION="${REGION:-us-central1}"
SERVICE_ACCOUNT_NAME="github-actions"
POOL_NAME="github-actions-pool"
PROVIDER_NAME="github-actions-provider"
GITHUB_OWNER="${GITHUB_OWNER:-Alejandro-Montepeque}"
GITHUB_REPO="${GITHUB_REPO:-job-matcher-agent}"

PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')

echo "Enabling required APIs..."
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  iamcredentials.googleapis.com \
  secretmanager.googleapis.com \
  --project="$PROJECT_ID"

echo "Creating service account..."
gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" \
  --display-name="GitHub Actions deployer" \
  --project="$PROJECT_ID" 2>/dev/null || true

SA_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "Granting roles to service account..."
for role in roles/run.admin roles/iam.serviceAccountUser roles/artifactregistry.writer roles/secretmanager.secretAccessor; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SA_EMAIL" \
    --role="$role" \
    --quiet
done

echo "Creating Workload Identity Pool..."
gcloud iam workload-identity-pools create "$POOL_NAME" \
  --location=global \
  --display-name="GitHub Actions Pool" \
  --project="$PROJECT_ID" 2>/dev/null || true

echo "Creating OIDC provider..."
gcloud iam workload-identity-pools providers create-oidc "$PROVIDER_NAME" \
  --location=global \
  --workload-identity-pool="$POOL_NAME" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" \
  --attribute-condition="assertion.repository_owner == '${GITHUB_OWNER}'" \
  --project="$PROJECT_ID" 2>/dev/null || true

echo "Binding service account to GitHub repo..."
gcloud iam service-accounts add-iam-policy-binding "$SA_EMAIL" \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_NAME}/attribute.repository/${GITHUB_OWNER}/${GITHUB_REPO}" \
  --project="$PROJECT_ID"

echo "Creating Artifact Registry repo..."
gcloud artifacts repositories create job-matcher \
  --repository-format=docker \
  --location="$REGION" \
  --project="$PROJECT_ID" 2>/dev/null || true

echo "Creating placeholder secret for Gemini API key..."
echo "REPLACE_WITH_YOUR_KEY" | gcloud secrets create gemini-api-key \
  --data-file=- \
  --project="$PROJECT_ID" 2>/dev/null || true

echo "Creating placeholder secret for database URL..."
echo "REPLACE_WITH_YOUR_NEON_URL" | gcloud secrets create database-url \
  --data-file=- \
  --project="$PROJECT_ID" 2>/dev/null || true

echo
echo "Done. Add these GitHub repo secrets:"
echo "  GCP_PROJECT_ID         = $PROJECT_ID"
echo "  GCP_SERVICE_ACCOUNT    = $SA_EMAIL"
echo "  GCP_WIF_PROVIDER       = projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_NAME}/providers/${PROVIDER_NAME}"
echo "  ALLOWED_ORIGINS        = https://your-frontend.vercel.app"
echo
echo "Then update the Secret Manager values with your real ones:"
echo "  echo -n YOUR_GEMINI_KEY | gcloud secrets versions add gemini-api-key --data-file=- --project=$PROJECT_ID"
echo "  echo -n YOUR_NEON_URL   | gcloud secrets versions add database-url   --data-file=- --project=$PROJECT_ID"
echo
echo "DATABASE_URL must use the asyncpg driver, for example:"
echo "  postgresql+asyncpg://user:pass@ep-xxx.neon.tech/jobmatcher?sslmode=require"
