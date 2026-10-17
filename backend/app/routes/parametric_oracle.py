"""
TERRA-SENTINEL: Multi-Sensor Parametric Oracle REST API Router
Phase 28: Autonomous Climate Risk Smart Contract Oracles for Web3 Parametric Payouts
"""

import logging
from typing import List
from fastapi import APIRouter
from backend.app.parametric_oracle import (
    parametric_oracle_engine,
    OracleConditionInput,
    OracleEvaluationResult,
    OracleSettlementResponse
)

logger = logging.getLogger("terra_sentinel.routes.parametric_oracle")

router = APIRouter(tags=["Multi-Sensor Parametric Oracle"])


@router.post("/oracle/evaluate-trigger", response_model=OracleEvaluationResult)
async def evaluate_parametric_trigger(inp: OracleConditionInput):
    """
    Evaluates multi-sensor tripartite condition invariant:
    (Depth_LoRa >= 100cm) AND (P_Clay >= 0.70) AND (Area_VEDA >= 5.0 sq km).
    """
    return parametric_oracle_engine.evaluate_trigger_conditions(inp)


@router.post("/oracle/auto-payout", response_model=OracleSettlementResponse)
async def execute_parametric_auto_payout(inp: OracleConditionInput):
    """
    Autonomous smart contract payout dispatcher.
    Upon positive condition satisfaction, executes micro-insurance relief settlement
    on Polygon Amoy blockchain and anchors metadata on IPFS.
    """
    return parametric_oracle_engine.execute_auto_settlement(inp)


@router.get("/oracle/history", response_model=List[OracleSettlementResponse])
async def get_oracle_settlement_history():
    """
    Retrieves history of all automated parametric payouts executed on-chain.
    """
    return parametric_oracle_engine.get_history()


@router.get("/oracle/health")
async def get_oracle_health():
    """Lightweight health probe for parametric oracle service."""
    return {
        "status": "operational",
        "service": "Multi-Sensor Parametric Catastrophe Oracle",
        "contract": parametric_oracle_engine.contract_address,
        "circuit_state": parametric_oracle_engine.circuit_state
    }
