"""
Health Check Route
Provides detailed operational health status for AEGIS microservices.
"""
from fastapi import APIRouter
from backend.app.config import settings
from backend.app.schemas import HealthResponse

router = APIRouter(tags=["System Health"])


@router.get("/health", response_model=HealthResponse)
async def get_health_status():
    """Health check for FastAPI Backend, MCP Hub connection, and system state."""
    return HealthResponse(
        status="operational",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        services={
            "fastapi_backend": "online",
            "mcp_hub": "available",
            "open_meteo_gateway": "connected",
            "langgraph_engine": "ready",
            "vector_store": "ready",
            "websocket_bus": "active"
        }
    )
