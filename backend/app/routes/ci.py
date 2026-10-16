"""
FastAPI Route Module: Phase 21 - Google Cloud Build Automation & CI/CD Pipeline
Endpoints:
  - GET  /ci/phase21/health
  - POST /ci/phase21/pipeline
  - POST /ci/validate/pipeline
  - GET  /ci/cloudbuild/config
  - POST /ci/simulate/trigger
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.cloud_ci import (
    CloudBuildModel,
    CIBuildStepRequest,
    CIBuildStepResult,
    evaluate_ci_pipeline_sequence,
    inspect_cloudbuild_yaml,
    simulate_ci_trigger,
    cloud_ci_controller
)

router = APIRouter(prefix="/ci", tags=["Phase 21 - Google Cloud Build Automation & CI/CD Pipeline"])


class TriggerSimulationRequest(BaseModel):
    branch: str = Field("main", description="Git branch name (e.g., 'main', 'feature/satellite')")
    commit_sha: str = Field("HEAD", description="Commit SHA or reference")


@router.get("/phase21/health")
async def ci_health_endpoint():
    """
    GET /ci/phase21/health
    Returns operational health status, circuit breaker state, and Cloud CI diagnostics.
    """
    return {
        "status": "healthy",
        "phase": 21,
        "name": "Google Cloud Build Automation (`cloudbuild.yaml`) & CI/CD Pipeline",
        "diagnostics": cloud_ci_controller.get_ci_diagnostics()
    }


@router.post("/phase21/pipeline", response_model=CloudBuildModel)
async def ci_pipeline_endpoint(payload: Dict[str, Any]):
    """
    POST /ci/phase21/pipeline
    Executes the standard Phase 21 Gravitas verification pipeline.
    """
    try:
        res = await cloud_ci_controller.execute_phase_pipeline(payload)
        return res
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"CI pipeline error: {str(exc)}")


@router.post("/validate/pipeline", response_model=CIBuildStepResult)
async def validate_pipeline_steps_endpoint(req: CIBuildStepRequest):
    """
    POST /ci/validate/pipeline
    Enforces governing invariant: GitPush(main) ==> Test ==> Build ==> Deploy(CloudRun).
    """
    try:
        return evaluate_ci_pipeline_sequence(steps=req.steps, branch=req.branch)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pipeline sequence validation failed: {str(exc)}")


@router.get("/cloudbuild/config")
async def get_cloudbuild_config_endpoint(yaml_path: Optional[str] = None):
    """
    GET /ci/cloudbuild/config
    Returns parsed cloudbuild.yaml structure, steps, and target deployment attributes.
    """
    return inspect_cloudbuild_yaml(yaml_path=yaml_path)


@router.post("/simulate/trigger")
async def simulate_trigger_endpoint(req: TriggerSimulationRequest):
    """
    POST /ci/simulate/trigger
    Simulates Git Push CI/CD trigger and returns deterministic deployment plan.
    """
    try:
        return simulate_ci_trigger(branch=req.branch, commit_sha=req.commit_sha)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"CI trigger simulation failed: {str(exc)}")
