"""
AEGIS-CLIMATE FastAPI Main Entrypoint
Autonomous Multi-Agent Environmental Intelligence Platform
Harden per PRD 2: E-001, E-008, E-009 (Strict CORS, Request ID, Safe Errors)
"""
import logging
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.config import settings
from backend.app.websocket import manager
from backend.app.middleware import RequestCorrelationMiddleware
from backend.app.errors import AEGISError, ErrorResponse
from backend.app.routes import health, analyze, geo, documents, hotspots, blockchain, evidence

# Resilient MCP Hub import — backend must never crash due to agent engine import failures
try:
    from mcp_hub.hub import router as mcp_router
    HAS_MCP_HUB = True
except Exception as _mcp_import_err:
    mcp_router = None
    HAS_MCP_HUB = False
    logging.getLogger("aegis.main").warning(f"MCP Hub import deferred (non-fatal): {_mcp_import_err}")

# Configure Logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("aegis.main")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Autonomous Multi-Agent Environmental & Climate Risk Intelligence Platform for Bharat",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Tracing & Security Middleware
app.add_middleware(RequestCorrelationMiddleware)

# CORS Configuration - Explicit origin allowlist (PRD 2 E-009)
origins = settings.ALLOWED_ORIGINS if isinstance(settings.ALLOWED_ORIGINS, list) else [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(AEGISError)
async def aegis_domain_exception_handler(request: Request, exc: AEGISError):
    """Handles structured domain errors without leaking internal stack traces."""
    correlation_id = getattr(request.state, "correlation_id", exc.correlation_id)
    logger.warning(f"Domain error [{exc.error_code}] on {request.url.path} (CID: {correlation_id}): {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_response().model_dump()
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catches all unexpected exceptions.
    Logs full exception details securely on the server with correlation ID,
    returning a sanitized, safe response to the client (PRD 2: E-009).
    """
    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
    logger.error(f"Unhandled exception on {request.url.path} (CID: {correlation_id}): {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected server error occurred. Please reference the correlation ID for diagnosis.",
            "correlation_id": correlation_id
        }
    )


# Mount API Routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(analyze.router, prefix="/api/v1")
app.include_router(geo.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(hotspots.router, prefix="/api/v1")
app.include_router(evidence.router, prefix="/api/v1")

# Mount AEGIS-CHAIN v2.0 Blockchain Gateway
app.include_router(blockchain.router, prefix="/api/v2")

if HAS_MCP_HUB and mcp_router:
    app.include_router(mcp_router)  # Model Context Protocol Gateway (/mcp/health, /mcp/tools, /mcp/invoke)


@app.get("/")
async def root():
    return {
        "platform": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "edition": "Enterprise Climate Intelligence",
        "docs": "/docs",
        "api_v1": "/api/v1",
        "api_v2": "/api/v2"
    }


@app.get("/health")
async def health_alias():
    return {
        "status": "operational",
        "version": settings.APP_VERSION,
        "platform": settings.APP_NAME
    }


@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time WebSocket stream for agent thought trace, tool invocations, and live alerts."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive & handle incoming pings
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
