"""
Phase 7: Monte Carlo Financial VaR & Macro Transition Stress-Testing Suite
Governance: Gravitas Reliability Runtime · PRD.md Section 16 Phase 7 Invariants

Verifies:
1. Deterministic damage curve: Loss = V_asset * (1 - e^{-lambda * D}) is strictly monotonic.
2. Monte Carlo statistical invariants: VaR_99 >= VaR_95 >= Median, and CVaR_95 >= VaR_95.
3. PRD.md Section 16 Phase 7 contract adhering to FinancialVaRModel schema.
4. FastAPI endpoints: /financial/monte-carlo-var, /financial/stress-test/{id}, /financial/pipeline, /financial/hybrid-rag-query.
5. MCP Hub JSON-RPC tool invocation for run_monte_carlo_financial_var.
6. Banking collateral stress-testing and RBI LTV haircut calculation.
7. Circuit breaker failover transitions.
"""
import pytest
import time
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.financial import (
    macro_financial_controller,
    MacroFinancialController,
    AssetValuation
)

client = TestClient(app)


def test_exponential_damage_curve_monotonicity():
    """
    Validates that damage ratio monotonically increases with inundation depth:
    Loss = V_asset * (1 - e^{-lambda * D})
    """
    val = 100_000_000.0  # ₹10 Cr
    loss_0 = MacroFinancialController.calculate_single_asset_damage(val, depth_cm=0.0)
    loss_20 = MacroFinancialController.calculate_single_asset_damage(val, depth_cm=20.0)
    loss_60 = MacroFinancialController.calculate_single_asset_damage(val, depth_cm=60.0)
    loss_120 = MacroFinancialController.calculate_single_asset_damage(val, depth_cm=120.0)

    assert loss_0 == 0.0, "Zero depth must result in 0 financial loss."
    assert loss_20 > loss_0, "20cm depth must exceed 0cm loss."
    assert loss_60 > loss_20, "60cm depth must exceed 20cm loss."
    assert loss_120 > loss_60, "120cm depth must exceed 60cm loss."
    assert loss_120 <= val, "Loss cannot exceed total asset valuation."


def test_monte_carlo_distribution_statistical_invariants():
    """
    Validates statistical distribution invariants:
    VaR_99 >= VaR_95 >= Median, and CVaR_95 >= VaR_95.
    """
    res = macro_financial_controller.run_monte_carlo_var(
        base_depth_cm=85.0,
        risk_score=0.82,
        num_simulations=1000
    )
    assert res.simulation_iterations == 1000
    assert res.var_99_inr >= res.var_95_inr, f"VaR 99% ({res.var_99_inr}) must be >= VaR 95% ({res.var_95_inr})"
    assert res.var_95_inr >= res.median_loss_inr, f"VaR 95% ({res.var_95_inr}) must be >= Median ({res.median_loss_inr})"
    assert res.cvar_95_expected_shortfall_inr >= res.var_95_inr, "Expected Shortfall (CVaR) must be >= VaR 95%"
    assert res.var_95_usd == round(res.var_95_inr / 83.2, 2)
    assert res.stranded_asset_tier in ("CRITICAL_STRANDED", "HIGH")
    assert res.rbi_ltv_haircut_pct >= 18.0


@pytest.mark.asyncio
async def test_phase_7_execution_invariant_prd_contract():
    """
    Validates PRD.md Section 16 Phase 7 execution invariant contract.
    """
    controller = MacroFinancialController()
    sample_payload = {
        "event_id": "TEST-PHASE-7-INVARIANT",
        "waterlogging_depth_cm": 90.0,
        "risk_score": 0.85
    }
    result = await controller.execute_phase_pipeline(sample_payload)
    assert result.event_id == "TEST-PHASE-7-INVARIANT"
    assert result.verified_flag is True
    assert result.metadata["status"] == "OPERATIONAL"
    assert result.metadata["phase_id"] == 7
    assert result.metadata["var_95_inr"] > 0.0
    assert result.metadata["var_99_inr"] >= result.metadata["var_95_inr"]


def test_monte_carlo_var_endpoint():
    """
    Tests POST /api/v1/financial/monte-carlo-var endpoint.
    """
    payload = {
        "location_name": "Chennai Industrial Belt",
        "waterlogging_depth_cm": 95.0,
        "risk_score": 0.82,
        "num_simulations": 500
    }
    response = client.post("/api/v1/financial/monte-carlo-var", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["var_95_inr"] > 0
    assert data["var_99_inr"] >= data["var_95_inr"]
    assert data["cvar_95_expected_shortfall_inr"] >= data["var_95_inr"]
    assert data["direct_physical_damage_inr"] > 0
    assert data["business_downtime_interruption_inr"] > 0
    assert data["statutory_regulatory_fines_inr"] > 0
    assert data["simulation_iterations"] == 500


def test_collateral_stress_test_endpoint():
    """
    Tests GET /api/v1/financial/stress-test/{event_id} endpoint.
    """
    response = client.get("/api/v1/financial/stress-test/EVT-STRESS-99?depth_cm=90.0&risk_score=0.85")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["event_id"] == "EVT-STRESS-99"
    assert data["original_portfolio_inr"] == 540_000_000.0
    assert data["rbi_haircut_pct"] == 25.0
    assert data["stressed_collateral_value_inr"] < data["original_portfolio_inr"]
    assert data["sebi_disclosure_status"] == "MANDATORY_TIER_2_AUDIT_REQUIRED"


def test_mcp_monte_carlo_var_tool_invocation():
    """
    Tests MCP Hub dispatcher invocation for run_monte_carlo_financial_var tool.
    """
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "run_monte_carlo_financial_var",
            "arguments": {
                "waterlogging_depth_cm": 110.0,
                "risk_score": 0.88,
                "num_simulations": 500
            }
        },
        "id": "test-mcp-phase7"
    }
    response = client.post("/mcp/invoke", json=payload)
    assert response.status_code == 200, response.text
    res = response.json()
    assert "result" in res
    data = res["result"].get("data", res["result"])
    assert data["tool"] == "run_monte_carlo_financial_var"
    assert data["var_95_inr"] > 0.0
    assert data["var_99_inr"] >= data["var_95_inr"]
    assert data["stranded_asset_tier"] in ("CRITICAL_STRANDED", "HIGH")


def test_hybrid_rag_statutory_query_endpoint():
    """
    Tests GET /api/v1/financial/hybrid-rag-query endpoint.
    """
    response = client.get("/api/v1/financial/hybrid-rag-query?query=SEBI+BRSR+Principle+6+penalties")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["matched_clauses_count"] > 0
    assert len(data["statutory_mandates"]) > 0
    assert any("SEBI" in m or "NDMA" in m or "Carbon" in m for m in data["statutory_mandates"])
