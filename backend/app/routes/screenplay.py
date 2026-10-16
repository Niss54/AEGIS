"""
FastAPI Route Module: Phase 24 - AI Builder Cup 3-Minute Video Demo Screenplay & Teleprompter Plan
Endpoints:
  - GET  /screenplay/phase24/health
  - POST /screenplay/phase24/pipeline
  - POST /screenplay/timing/evaluate
  - GET  /screenplay/script/audit
  - GET  /screenplay/teleprompter/cues
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.screenplay import (
    DemoScreenplayModel,
    ScreenplayTimingRequest,
    ScreenplayTimingResult,
    evaluate_screenplay_timing_budget,
    parse_and_validate_demo_script,
    generate_teleprompter_cue_sheet,
    screenplay_controller
)

router = APIRouter(prefix="/screenplay", tags=["Phase 24 - AI Builder Cup 3-Minute Video Demo Screenplay"])


@router.get("/phase24/health")
async def screenplay_health_endpoint():
    """
    GET /screenplay/phase24/health
    Returns operational health status, circuit breaker state, and Screenplay diagnostics.
    """
    return {
        "status": "healthy",
        "phase": 24,
        "name": "AI Builder Cup 3-Minute Video Demo Screenplay & Teleprompter Plan",
        "diagnostics": screenplay_controller.get_screenplay_diagnostics()
    }


@router.post("/phase24/pipeline", response_model=DemoScreenplayModel)
async def screenplay_pipeline_endpoint(payload: Dict[str, Any]):
    """
    POST /screenplay/phase24/pipeline
    Executes the standard Phase 24 Gravitas verification pipeline.
    """
    try:
        res = await screenplay_controller.execute_phase_pipeline(payload)
        return res
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Screenplay pipeline error: {str(exc)}")


@router.post("/timing/evaluate", response_model=ScreenplayTimingResult)
async def evaluate_timing_endpoint(req: ScreenplayTimingRequest):
    """
    POST /screenplay/timing/evaluate
    Enforces governing invariant: Delta_t = 30s + 60s + 60s + 30s = 180s.
    """
    try:
        return evaluate_screenplay_timing_budget(
            act1_crisis_s=req.act1_crisis_s,
            act2_ui_s=req.act2_ui_s,
            act3_cloud_s=req.act3_cloud_s,
            act4_roi_s=req.act4_roi_s
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Timing budget evaluation failed: {str(exc)}")


@router.get("/script/audit")
async def audit_script_endpoint(script_path: Optional[str] = None):
    """
    GET /screenplay/script/audit
    Returns static audit of docs/DEMO_SCRIPT.md (Act breakdown, Google Cloud keywords, word count).
    """
    return parse_and_validate_demo_script(script_path=script_path)


@router.get("/teleprompter/cues")
async def teleprompter_cues_endpoint():
    """
    GET /screenplay/teleprompter/cues
    Returns structured teleprompter cue sheet for the 3-minute video presentation.
    """
    return generate_teleprompter_cue_sheet()
