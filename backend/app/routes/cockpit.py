"""
FastAPI Route Module: Phase 18 - Mission-Control Cockpit
(React 19 + TypeScript + Leaflet CartoDB 60fps)
Endpoints:
  - GET  /cockpit/phase18/health
  - POST /cockpit/phase18/pipeline
  - POST /cockpit/frame-budget/evaluate
  - POST /cockpit/contours/optimize
  - GET  /cockpit/state
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.web_cockpit import (
    FrontendViewModel,
    FrameBudgetEvaluationRequest,
    FrameBudgetResult,
    evaluate_frame_budget,
    optimize_gis_contour_vectors,
    web_cockpit_controller
)

router = APIRouter(prefix="/cockpit", tags=["Phase 18 - Mission-Control Cockpit"])


class ContourOptimizationRequest(BaseModel):
    geojson_data: Dict[str, Any] = Field(..., description="GeoJSON FeatureCollection containing polygons")
    max_vertices: int = Field(3000, ge=100, le=50000, description="Upper vertex budget to guarantee 60fps")


@router.get("/phase18/health")
async def cockpit_health_endpoint():
    """
    GET /cockpit/phase18/health
    Returns operational health status, circuit breaker state, and 60fps benchmark history.
    """
    return {
        "status": "healthy",
        "phase": 18,
        "name": "Mission-Control Cockpit (React 19 + TypeScript + Leaflet CartoDB 60fps)",
        "diagnostics": web_cockpit_controller.get_cockpit_state()
    }


@router.post("/phase18/pipeline", response_model=FrontendViewModel)
async def cockpit_pipeline_endpoint(payload: Dict[str, Any]):
    """
    POST /cockpit/phase18/pipeline
    Executes the standard Phase 18 Gravitas verification pipeline.
    """
    try:
        res = await web_cockpit_controller.execute_phase_pipeline(payload)
        return res
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Cockpit pipeline error: {str(exc)}")


@router.post("/frame-budget/evaluate", response_model=FrameBudgetResult)
async def evaluate_frame_budget_endpoint(req: FrameBudgetEvaluationRequest):
    """
    POST /cockpit/frame-budget/evaluate
    Enforces governing invariant: FrameBudget <= 16.67ms ==> FPS >= 60.
    """
    try:
        return evaluate_frame_budget(
            render_time_ms=req.render_time_ms,
            vertex_count=req.vertex_count
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(exc)}")


@router.post("/contours/optimize")
async def optimize_contours_endpoint(req: ContourOptimizationRequest):
    """
    POST /cockpit/contours/optimize
    Simplifies high-density GeoJSON contours to prevent frame budget violations.
    """
    try:
        return optimize_gis_contour_vectors(
            geojson_data=req.geojson_data,
            max_vertices=req.max_vertices
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Contour decimation failed: {str(exc)}")


@router.get("/state")
async def cockpit_state_endpoint():
    """
    GET /cockpit/state
    Returns the real-time GIS layer configuration, tileset status, and frame target.
    """
    return web_cockpit_controller.get_cockpit_state()
