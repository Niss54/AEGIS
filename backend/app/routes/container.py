"""
FastAPI Route Module: Phase 20 - Multi-Stage Dockerfile Hardening & Google Cloud Run Packaging
Endpoints:
  - GET  /container/phase20/health
  - POST /container/phase20/pipeline
  - POST /container/spec/validate
  - GET  /container/cloudrun/spec
  - GET  /container/dockerfile/inspect
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.docker_package import (
    ContainerPackageModel,
    ContainerBudgetRequest,
    ContainerBudgetResult,
    evaluate_container_image_budget,
    inspect_dockerfile_security,
    get_cloud_run_spec,
    docker_packaging_controller
)

router = APIRouter(prefix="/container", tags=["Phase 20 - Multi-Stage Dockerfile Hardening & Cloud Run Packaging"])


@router.get("/phase20/health")
async def container_health_endpoint():
    """
    GET /container/phase20/health
    Returns operational health status, circuit breaker state, and container packaging diagnostics.
    """
    return {
        "status": "healthy",
        "phase": 20,
        "name": "Multi-Stage Dockerfile Hardening & Google Cloud Run Serverless Packaging",
        "diagnostics": docker_packaging_controller.get_packaging_diagnostics()
    }


@router.post("/phase20/pipeline", response_model=ContainerPackageModel)
async def container_pipeline_endpoint(payload: Dict[str, Any]):
    """
    POST /container/phase20/pipeline
    Executes the standard Phase 20 Gravitas verification pipeline.
    """
    try:
        res = await docker_packaging_controller.execute_phase_pipeline(payload)
        return res
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Container pipeline error: {str(exc)}")


@router.post("/spec/validate", response_model=ContainerBudgetResult)
async def validate_container_spec_endpoint(req: ContainerBudgetRequest):
    """
    POST /container/spec/validate
    Enforces governing invariant: ImageSize <= 250MB, Vulnerabilities = 0.
    """
    try:
        return evaluate_container_image_budget(
            image_size_mb=req.image_size_mb,
            vulnerability_count=req.vulnerability_count,
            non_root_user=req.non_root_user
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Container budget evaluation failed: {str(exc)}")


@router.get("/cloudrun/spec")
async def get_cloudrun_spec_endpoint():
    """
    GET /container/cloudrun/spec
    Returns serverless Google Cloud Run deployment configuration specification.
    """
    return get_cloud_run_spec()


@router.get("/dockerfile/inspect")
async def inspect_dockerfile_endpoint(path: Optional[str] = None):
    """
    GET /container/dockerfile/inspect
    Statically analyzes Dockerfile security directives (multi-stage, non-root user UID 10001, healthcheck, etc.).
    """
    return inspect_dockerfile_security(dockerfile_path=path)
