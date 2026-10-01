"""
AEGIS-CLIMATE FastAPI Main Entrypoint
Autonomous Multi-Agent Environmental Intelligence Platform
"""
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.websocket import manager
from backend.app.routes import health, analyze, geo, documents, hotspots
from mcp_hub.hub import router as mcp_router

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

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(analyze.router, prefix="/api/v1")
app.include_router(geo.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(hotspots.router, prefix="/api/v1")
app.include_router(mcp_router)  # Model Context Protocol Gateway (/mcp/health, /mcp/tools, /mcp/invoke)


@app.get("/")
async def root():
    return {
        "platform": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "hackathon": "BHARAT AGENTIC 2026 (AIKart)",
        "team": "Syntrix",
        "docs": "/docs",
        "api_v1": "/api/v1"
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
