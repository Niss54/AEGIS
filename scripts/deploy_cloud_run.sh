#!/usr/bin/env bash
# ==============================================================================
# AEGIS-CLIMATE: Google Cloud Run One-Command Deployment Script
# Built for IEEE ClimateChain 2026 (Track 4)
# ==============================================================================
set -euo pipefail

PROJECT_ID=${GCP_PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || echo "")}
REGION=${GCP_REGION:-"asia-south1"}
SERVICE_NAME="aegis-climate"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

if [ -z "$PROJECT_ID" ]; then
    echo "ERROR: GCP_PROJECT_ID is not set. Run 'gcloud config set project YOUR_PROJECT_ID'"
    exit 1
fi

echo "🚀 Deploying ${SERVICE_NAME} to Google Cloud Run in ${REGION} (Project: ${PROJECT_ID})..."

# 1. Build and Submit to Google Container Registry
echo "📦 Building container image..."
gcloud builds submit --tag "${IMAGE_NAME}" .

# 2. Deploy to Cloud Run
echo "☁️ Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
    --image "${IMAGE_NAME}" \
    --platform managed \
    --region "${REGION}" \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --port 8080 \
    --set-env-vars ENVIRONMENT=production,DEBUG=false,APP_NAME=AEGIS-CLIMATE

# 3. Retrieve URL
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --platform managed --region "${REGION}" --format 'value(status.url)')
echo "✅ Deployment complete!"
echo "🌐 Live Production Service URL: ${SERVICE_URL}"
echo "📄 Swagger API Documentation: ${SERVICE_URL}/docs"
