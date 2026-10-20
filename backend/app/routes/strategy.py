"""
AEGIS-CLIMATE REST API Router: Phase 25
Module: backend.app.routes.strategy
Focus: 10-Slide Executive VC Pitch Deck, TAM/SAM/SOM & Grand Finale Strategy
"""
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.finale_strategy import (
    FinaleStrategyController,
    ExecutivePitchModel,
    TAMMarketRequest,
    MarketOpportunityResult,
    evaluate_tam_sam_som_market_opportunity,
    audit_pitch_deck_structure,
    generate_singapore_grand_finale_playbook
)

logger = logging.getLogger("aegis.routes.strategy")

router = APIRouter(prefix="/strategy", tags=["Phase 25: Executive VC Strategy & Grand Finale"])
controller = FinaleStrategyController()


class StrategyHealthResponse(BaseModel):
    phase_id: int = 25
    name: str
    status: str
    circuit_breaker: Dict[str, Any]
    governing_equation: str = "TAM = $12.8B, SAM = $3.2B, SOM = $480M"


class PitchDeckAuditResponse(BaseModel):
    status: str = "success"
    audit: Dict[str, Any]


@router.get("/phase25/health", response_model=StrategyHealthResponse)
def get_strategy_health() -> StrategyHealthResponse:
    """Returns runtime health status and circuit breaker telemetry for Phase 25."""
    circuit_status = controller.get_circuit_status()
    return StrategyHealthResponse(
        phase_id=25,
        name=controller.name,
        status="OPERATIONAL",
        circuit_breaker=circuit_status,
        governing_equation="TAM = $12.8B, SAM = $3.2B, SOM = $480M"
    )


@router.post("/phase25/pipeline", response_model=ExecutivePitchModel)
async def run_strategy_pipeline(payload: Dict[str, Any]) -> ExecutivePitchModel:
    """Executes the Phase 25 finale strategy pipeline with circuit-breaker protection."""
    try:
        return await controller.execute_phase_pipeline(payload)
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Pipeline error: {str(exc)}")


@router.post("/tam/evaluate", response_model=MarketOpportunityResult)
def evaluate_tam_endpoint(request: TAMMarketRequest) -> MarketOpportunityResult:
    """
    Evaluates TAM/SAM/SOM market opportunity against governing constraints:
    TAM = $12.8B, SAM = $3.2B, SOM = $480M.
    """
    return evaluate_tam_sam_som_market_opportunity(
        tam_usd_b=request.tam_usd_b,
        sam_usd_b=request.sam_usd_b,
        som_usd_m=request.som_usd_m
    )


@router.get("/deck/audit", response_model=PitchDeckAuditResponse)
def audit_pitch_deck_endpoint(deck_path: Optional[str] = None) -> PitchDeckAuditResponse:
    """Statically verifies the 10-slide canonical investor deck and Google Cloud differentiators."""
    audit_res = audit_pitch_deck_structure(deck_path)
    return PitchDeckAuditResponse(status="success", audit=audit_res)


@router.get("/grandfinale/playbook")
def get_grand_finale_playbook_endpoint(event_name: Optional[str] = None) -> Dict[str, Any]:
    """Retrieves the Singapore Grand Finale 48-Hour Live Demo Execution Playbook."""
    event = event_name or "Google Cloud AI Builder Cup — JAPAC Grand Finale"
    return {
        "status": "success",
        "playbook": generate_singapore_grand_finale_playbook(event_name=event)
    }
