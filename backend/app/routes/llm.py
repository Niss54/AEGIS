"""
TERRA-SENTINEL REST API: Phase 10 LLM Resilience & Circuit Breaker Gateway
Exposes real-time circuit breaker status and resilient multi-model routing endpoints.
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.llm_circuit import llm_circuit_controller, LLMFailoverModel

router = APIRouter(prefix="/llm", tags=["Multi-Model LLM Resilience & Circuit Breaker"])


class RoutePromptRequest(BaseModel):
    prompt: str = Field(..., description="Prompt or query to evaluate")
    preferred_tier: int = Field(1, ge=1, le=5, description="Preferred starting tier (1: Gemini, 2: Groq, 3: Claude, 4: OpenAI, 5: Local)")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Contextual metadata for grounding")
    mock_failures: Optional[List[int]] = Field(default_factory=list, description="List of tier IDs to simulate failures for testing")


@router.get("/circuit-status")
async def get_circuit_status():
    """
    Returns real-time health and state machine metrics for all 5 hierarchical LLM tiers.
    Adheres to State(t) = OPEN if Failures_60s >= 3 else CLOSED.
    """
    return llm_circuit_controller.get_circuit_status()


@router.post("/route-prompt")
async def route_llm_prompt(request: RoutePromptRequest):
    """
    Routes prompt across the 5-tier resilience hierarchy with automatic circuit breaker failover.
    """
    try:
        result = llm_circuit_controller.route_prompt(
            prompt=request.prompt,
            preferred_tier=request.preferred_tier,
            context=request.context,
            mock_failures=request.mock_failures
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pipeline", response_model=LLMFailoverModel)
async def execute_phase10_pipeline(payload: Dict[str, Any]):
    """
    Executes standard PRD Phase 10 pipeline returning compliant LLMFailoverModel.
    """
    try:
        return await llm_circuit_controller.execute_phase_pipeline(payload)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset-circuits")
async def reset_circuits():
    """Resets all tier circuit breakers to CLOSED."""
    for breaker in llm_circuit_controller.tiers.values():
        breaker.state = "CLOSED"
        breaker.failure_timestamps.clear()
        breaker.last_failure_time = 0.0
    return {"status": "SUCCESS", "message": "All 5 LLM circuit breakers reset to CLOSED"}
