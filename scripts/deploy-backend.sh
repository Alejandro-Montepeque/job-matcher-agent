#!/usr/bin/env bash
# Manual backend deploy. Useful for first deploy or debugging.
# Requires: gcloud authenticated, Docker running locally.

set -euo pipefail

PROJECT_ID="${PROJECT_ID:-job-matcher-agent}"
REGION="${REGION:-us-central1}"
SERVICE="job-matcher-api"
REPO="job-matcher"
IMAGE_NAME="api"
TAG="${1:-manual-$(date +%Y%m%d-%H%M%S)}"

IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${IMAGE_NAME}"

echo "Building $IMAGE:$TAG"
docker build -t "$IMAGE:$TAG" -t "$IMAGE:latest" backend

echo "Pushing $IMAGE:$TAG"
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet
docker push "$IMAGE:$TAG"
docker push "$IMAGE:latest"

echo "Deploying to Cloud Run"
gcloud run deploy "$SERVICE" \
  --image="$IMAGE:$TAG" \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --platform=managed \
  --allow-unauthenticated \
  --port=8080 \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=3 \
  --set-secrets=GEMINI_API_KEY=gemini-api-key:latest,DATABASE_URL=database-url:latest

gcloud run services describe "$SERVICE" \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --format='value(status.url)'
