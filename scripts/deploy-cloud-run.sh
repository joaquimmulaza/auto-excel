#!/usr/bin/env bash
# Deploy Cotarco FastAPI backend to Google Cloud Run.
# Requires: gcloud authenticated, billing enabled, APIs enabled.
#
# Usage:
#   export GCP_PROJECT_ID=your-project
#   export GCP_REGION=europe-west1
#   ./scripts/deploy-cloud-run.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT_ID="${GCP_PROJECT_ID:?Set GCP_PROJECT_ID}"
REGION="${GCP_REGION:-europe-west1}"
SERVICE="${CLOUD_RUN_SERVICE:-cotarco-ccm-api}"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/cotarco/${SERVICE}:latest"

echo "==> Project=${PROJECT_ID} Region=${REGION} Service=${SERVICE}"

gcloud config set project "${PROJECT_ID}"

gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com

gcloud artifacts repositories describe cotarco --location="${REGION}" >/dev/null 2>&1 \
  || gcloud artifacts repositories create cotarco \
       --repository-format=docker \
       --location="${REGION}" \
       --description="Cotarco CCM images"

echo "==> Building image ${IMAGE}"
gcloud builds submit "${ROOT}" \
  --tag "${IMAGE}" \
  --timeout=1200s

echo "==> Deploying Cloud Run service"
# Secrets must already exist in Secret Manager (do not pass raw secrets here).
gcloud run deploy "${SERVICE}" \
  --image="${IMAGE}" \
  --region="${REGION}" \
  --platform=managed \
  --allow-unauthenticated \
  --memory=1Gi \
  --cpu=1 \
  --timeout=300 \
  --concurrency=20 \
  --min-instances=0 \
  --max-instances=3 \
  --set-env-vars="ENVIRONMENT=production,AUTH_MODE=supabase,STORAGE_BACKEND=supabase,STORAGE_BUCKET=job-files" \
  --set-secrets="DATABASE_URL=cotarco-database-url:latest,SUPABASE_URL=cotarco-supabase-url:latest,SUPABASE_ANON_KEY=cotarco-supabase-anon:latest,SUPABASE_SERVICE_ROLE_KEY=cotarco-supabase-service-role:latest,SUPABASE_JWT_SECRET=cotarco-supabase-jwt-secret:latest,GEMINI_API_KEY=cotarco-gemini-api-key:latest,ALLOWED_ORIGINS=cotarco-allowed-origins:latest"

URL="$(gcloud run services describe "${SERVICE}" --region="${REGION}" --format='value(status.url)')"
echo "==> Service URL: ${URL}"
echo "==> Health: ${URL}/health"
echo "==> Docs:   ${URL}/docs"
echo "==> Set NEXT_PUBLIC_API_URL=${URL}/api/v1 on Vercel"
