"""
FastAPI Route Module: Phase 22 - Vercel Edge Global Frontend Deployment & CDN Orchestration
Endpoints:
  - GET  /vercel/phase22/health
  - POST /vercel/phase22/pipeline
  - POST /vercel/performance/evaluate
  - GET  /vercel/config/inspect
  - GET  /vercel/cdn/routing
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.vercel_edge import (
    VercelEdgeModel,
    EdgePerformanceBudgetRequest,
    EdgePerformanceBudgetResult,
    evaluate_edge_performance_budget,
    inspect_vercel_configuration,
    get_edge_cdn_routing_spec,
    vercel_edge_controller
)

router = APIRouter(prefix="/vercel", tags=["Phase 22 - Vercel Edge Global Frontend Deployment & CDN Orchestration"])


@router.get("/phase22/health")
async def vercel_health_endpoint():
    """
    GET /vercel/phase22/health
    Returns operational health status, circuit breaker state, and Vercel edge diagnostics.
    """
    return {
        "status": "healthy",
        "phase": 22,
        "name": "Vercel Edge Global Frontend Deployment & CDN Orchestration",
        "diagnostics": vercel_edge_controller.get_edge_diagnostics()
    }


@router.post("/phase22/pipeline", response_model=VercelEdgeModel)
async def vercel_pipeline_endpoint(payload: Dict[str, Any]):
    """
    POST /vercel/phase22/pipeline
    Executes the standard Phase 22 Gravitas verification pipeline.
    """
    try:
        res = await vercel_edge_controller.execute_phase_pipeline(payload)
        return res
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Vercel edge pipeline error: {str(exc)}")


@router.post("/performance/evaluate", response_model=EdgePerformanceBudgetResult)
async def evaluate_performance_endpoint(req: EdgePerformanceBudgetRequest):
    """
    POST /vercel/performance/evaluate
    Enforces governing invariant: TTFB_global <= 80ms, LighthouseScore >= 98.
    """
    try:
        return evaluate_edge_performance_budget(
            ttfb_ms=req.ttfb_ms,
            lighthouse_score=req.lighthouse_score,
            edge_region=req.edge_region
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Edge performance evaluation failed: {str(exc)}")


@router.get("/config/inspect")
async def inspect_config_endpoint(path: Optional[str] = None):
    """
    GET /vercel/config/inspect
    Statically analyzes vercel.json for reverse proxy rules, immutable cache headers, and HSTS.
    """
    return inspect_vercel_configuration(config_path=path)


@router.get("/cdn/routing")
async def get_cdn_routing_endpoint():
    """
    GET /vercel/cdn/routing
    Returns production Anycast Edge CDN point-of-presence topology and SLA matrix.
    """
    return get_edge_cdn_routing_spec()
