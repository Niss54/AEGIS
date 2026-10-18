"""
Macro Transition & Financial Value-at-Risk Router
Provides Monte Carlo VaR simulation, banking collateral stress-testing, and statutory RAG query endpoints.
"""
import time
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException

from backend.app.financial import (
    macro_financial_controller,
    MonteCarloVaRRequest,
    VaRDistributionResult,
    FinancialVaRModel
)
from backend.app.agent3_financial import financial_risk_engine

router = APIRouter(prefix="/financial", tags=["Macro Transition & Financial VaR"])


@router.post("/monte-carlo-var", response_model=VaRDistributionResult)
async def calculate_monte_carlo_var(req: MonteCarloVaRRequest):
    """
    Executes N >= 1000 Monte Carlo iterations translating physical waterlogging depth into
    portfolio Value-at-Risk (VaR 95%, VaR 99%, Expected Shortfall CVaR, RBI LTV Haircuts).
    """
    try:
        return macro_financial_controller.run_monte_carlo_var(
            base_depth_cm=req.waterlogging_depth_cm,
            risk_score=req.risk_score,
            num_simulations=req.num_simulations,
            portfolio=req.asset_portfolio
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Monte Carlo VaR execution failed: {str(exc)}")


@router.get("/stress-test/{event_id}")
async def get_collateral_stress_test(
    event_id: str,
    depth_cm: float = 85.0,
    risk_score: float = 0.78,
    portfolio_valuation_inr: float = 540_000_000.0  # ₹54 Crores
):
    """
    Performs collateral stress test under RBI climate risk guidelines and SEBI BRSR Principle 6.
    """
    var_res = macro_financial_controller.run_monte_carlo_var(
        base_depth_cm=depth_cm,
        risk_score=risk_score,
        num_simulations=500
    )
    haircut_amount = round(portfolio_valuation_inr * (var_res.rbi_ltv_haircut_pct / 100.0), 2)
    stressed_collateral_value = round(portfolio_valuation_inr - haircut_amount, 2)

    return {
        "event_id": event_id,
        "original_portfolio_inr": portfolio_valuation_inr,
        "rbi_haircut_pct": var_res.rbi_ltv_haircut_pct,
        "collateral_haircut_inr": haircut_amount,
        "stressed_collateral_value_inr": stressed_collateral_value,
        "var_95_inr": var_res.var_95_inr,
        "var_99_inr": var_res.var_99_inr,
        "expected_shortfall_cvar_inr": var_res.cvar_95_expected_shortfall_inr,
        "stranded_asset_tier": var_res.stranded_asset_tier,
        "sebi_disclosure_status": "MANDATORY_TIER_2_AUDIT_REQUIRED" if var_res.var_95_inr > 50_000_000 else "STANDARD_DISCLOSURE"
    }


@router.post("/pipeline", response_model=FinancialVaRModel)
async def execute_phase7_pipeline(payload: Dict[str, Any]):
    """
    Standard PRD.md Section 16 Phase 7 Execution Pipeline returning FinancialVaRModel.
    """
    try:
        return await macro_financial_controller.execute_phase_pipeline(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Phase 7 pipeline execution failed: {str(exc)}")


@router.get("/hybrid-rag-query")
async def query_statutory_hybrid_rag(query: str = "SEBI BRSR carbon tax flood disclosure penalties"):
    """
    Hybrid statutory RAG query fusing vector embeddings with statutory corpus.
    """
    try:
        clauses = financial_risk_engine.rag.query(query, top_k=3)
        return {
            "query": query,
            "matched_clauses_count": len(clauses),
            "clauses": clauses,
            "statutory_mandates": [c["metadata"].get("title") for c in clauses]
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Hybrid RAG query failure: {str(exc)}")
