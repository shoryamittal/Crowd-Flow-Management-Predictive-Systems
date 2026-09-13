#!/usr/bin/env bash
# ==============================================================================
# SENTINEL-AI — Google Cloud Run Automated Deployment Script
# Google Cloud AI Builder Cup 2026 (Sustainability & Social Impact)
# ==============================================================================

set -euo pipefail

# Configuration Defaults
SERVICE_NAME="sentinel-ai"
REGION="${GOOGLE_CLOUD_LOCATION:-asia-south1}"
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project 2>/dev/null || true)}"
MEMORY="2Gi"
CPU="2"
MIN_INSTANCES="0"
MAX_INSTANCES="5"
TIMEOUT="300"
PORT="8080"

echo "=================================================================="
echo "🚀 Deploying SENTINEL-AI to Google Cloud Run"
echo "=================================================================="
echo "Service:  ${SERVICE_NAME}"
echo "Region:   ${REGION}"
echo "Project:  ${PROJECT_ID}"
echo "Memory:   ${MEMORY} | CPU: ${CPU}"
echo "Port:     ${PORT}"
echo "=================================================================="

if [ -z "${PROJECT_ID}" ]; then
  echo "❌ Error: GOOGLE_CLOUD_PROJECT is not set and no gcloud default project found."
  echo "Run: gcloud config set project YOUR_PROJECT_ID"
  exit 1
fi

# Ensure required Google Cloud services are enabled
echo "📦 Verifying required Google Cloud APIs..."
gcloud services enable run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    aiplatform.googleapis.com \
    --project "${PROJECT_ID}"

# Deploy directly from source using Google Cloud Buildpack & Dockerfile
echo "🔨 Building container and deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
    --source . \
    --region "${REGION}" \
    --project "${PROJECT_ID}" \
    --platform managed \
    --allow-unauthenticated \
    --port "${PORT}" \
    --memory "${MEMORY}" \
    --cpu "${CPU}" \
    --min-instances "${MIN_INSTANCES}" \
    --max-instances "${MAX_INSTANCES}" \
    --timeout "${TIMEOUT}" \
    --set-env-vars="HOST=0.0.0.0,PORT=${PORT},SENTINEL_AUTH_ENABLED=true,GOOGLE_CLOUD_PROJECT=${PROJECT_ID}"

echo ""
echo "✅ SENTINEL-AI deployed successfully to Google Cloud Run!"
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --platform managed --region "${REGION}" --project "${PROJECT_ID}" --format="value(status.url)")
echo "🌐 Live Service URL: ${SERVICE_URL}"
echo "🏥 Liveness Probe:    ${SERVICE_URL}/health"
echo "🛡️ Readiness Probe:   ${SERVICE_URL}/readiness"
echo "🤖 Copilot Status:   ${SERVICE_URL}/api/copilot/status"
