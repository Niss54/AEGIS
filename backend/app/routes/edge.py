"""
FastAPI Route Module: Phase 19 - Edge Network Resilience
(Service Worker & Local Storage Fallback)
Endpoints:
  - GET  /edge/phase19/health
  - POST /edge/phase19/pipeline
  - POST /edge/availability/evaluate
  - POST /edge/reconcile
  - GET  /edge/manifest
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.edge_worker import (
    PWAWorkerModel,
    EdgeAvailabilityRequest,
    EdgeAvailabilityResult,
    evaluate_edge_availability,
    reconcile_offline_queue,
    edge_worker_controller,
    PWA_CACHE_NAME
)

router = APIRouter(prefix="/edge", tags=["Phase 19 - Edge Network Resilience"])


class OfflineReconciliationRequest(BaseModel):
    mutations: List[Dict[str, Any]] = Field(default_factory=list, description="Array of queued mutations buffered offline")


@router.get("/phase19/health")
async def edge_health_endpoint():
    """
    GET /edge/phase19/health
    Returns operational health status, circuit breaker state, and PWA edge diagnostics.
    """
    return {
        "status": "healthy",
        "phase": 19,
        "name": "Edge Network Resilience (Service Worker & Local Storage Fallback)",
        "diagnostics": edge_worker_controller.get_edge_diagnostics()
    }


@router.post("/phase19/pipeline", response_model=PWAWorkerModel)
async def edge_pipeline_endpoint(payload: Dict[str, Any]):
    """
    POST /edge/phase19/pipeline
    Executes the standard Phase 19 Gravitas verification pipeline.
    """
    try:
        res = await edge_worker_controller.execute_phase_pipeline(payload)
        return res
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Edge pipeline error: {str(exc)}")


@router.post("/availability/evaluate", response_model=EdgeAvailabilityResult)
async def evaluate_availability_endpoint(req: EdgeAvailabilityRequest):
    """
    POST /edge/availability/evaluate
    Enforces governing invariant: Availability = 100% (Cached Shell ⊕ Local Heuristics).
    """
    try:
        return evaluate_edge_availability(
            is_online=req.is_online,
            has_cached_shell=req.has_cached_shell,
            has_local_heuristics=req.has_local_heuristics
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Availability evaluation failed: {str(exc)}")


@router.post("/reconcile")
async def reconcile_offline_mutations_endpoint(req: OfflineReconciliationRequest):
    """
    POST /edge/reconcile
    Reconciles queued client mutations created during network partitions.
    """
    try:
        return reconcile_offline_queue(req.mutations)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Reconciliation error: {str(exc)}")


@router.get("/manifest")
async def pwa_manifest_endpoint():
    """
    GET /edge/manifest
    Returns PWA Web App Manifest metadata for offline installation.
    """
    return {
        "short_name": "TERRA-SENTINEL",
        "name": "TERRA-SENTINEL: Autonomous Climate Risk Intelligence Platform",
        "description": "Enterprise Climate & Environmental Risk Intelligence Cockpit with 100% Offline Edge Availability",
        "icons": [
            {
                "src": "/favicon.svg",
                "type": "image/svg+xml",
                "sizes": "192x192 512x512"
            }
        ],
        "start_url": "/",
        "background_color": "#020617",
        "theme_color": "#020617",
        "display": "standalone",
        "orientation": "any",
        "cache_name": PWA_CACHE_NAME
    }
