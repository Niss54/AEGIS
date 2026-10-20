# ==============================================================================
# TERRA-SENTINEL: Google Cloud Run Windows PowerShell Deployment Script
# Built for AI Builder Cup 2026 (Sponsored by Google Cloud)
# ==============================================================================
param(
    [string]$ProjectId = $env:GCP_PROJECT_ID,
    [string]$Region = "asia-south1"
)

if (-not $ProjectId) {
    $ProjectId = (gcloud config get-value project 2>$null)
}

if (-not $ProjectId) {
    Write-Error "ERROR: GCP_PROJECT_ID is not set. Run 'gcloud config set project YOUR_PROJECT_ID'"
    exit 1
}

$ServiceName = "terra-sentinel"
$ImageName = "gcr.io/$ProjectId/${ServiceName}:latest"

Write-Host "🚀 Deploying $ServiceName to Google Cloud Run in $Region (Project: $ProjectId)..." -ForegroundColor Cyan

# 1. Build and Submit to Google Container Registry
Write-Host "📦 Building container image via Google Cloud Build..." -ForegroundColor Yellow
gcloud builds submit --tag $ImageName .

# 2. Deploy to Cloud Run
Write-Host "☁️ Deploying service to Google Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $ServiceName `
    --image $ImageName `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --memory 1Gi `
    --cpu 1 `
    --port 8080 `
    --set-env-vars ENVIRONMENT=production,DEBUG=false,APP_NAME=TERRA-SENTINEL

# 3. Retrieve URL
$ServiceUrl = (gcloud run services describe $ServiceName --platform managed --region $Region --format 'value(status.url)')
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🌐 Live Production Service URL: $ServiceUrl" -ForegroundColor Cyan
Write-Host "📄 Swagger API Documentation: $ServiceUrl/docs" -ForegroundColor Cyan
