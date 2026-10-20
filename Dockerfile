# Stage 1: Build Frontend Assets
FROM node:20-alpine AS frontend-builder
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci --prefer-offline --no-audit || npm install
COPY frontend/ ./
RUN npm run build || mkdir -p dist

# Stage 2: Hardened Python Production Environment
FROM python:3.12-slim

WORKDIR /app

# Minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (layer caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application backend and MCP hub
COPY backend /app/backend
COPY mcp_hub /app/mcp_hub
COPY --from=frontend-builder /build/dist /app/frontend/dist

# Security hardening: Create non-root user (UID 10001)
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh -m appuser && \
    chown -R appuser:appgroup /app

USER appuser

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

ENV PORT=8080
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8080}/api/v1/health || exit 1

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1 --timeout-keep-alive 30"]
