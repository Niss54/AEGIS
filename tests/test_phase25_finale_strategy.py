"""
AEGIS-CLIMATE Phase 25 Verification Test Suite
10-Slide Executive VC Pitch Deck, TAM/SAM/SOM & Grand Finale Strategy
Governance: Gravitas Reliability Runtime · Mathematical Invariant Verification
"""
import os
import time
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.finale_strategy import (
    FinaleStrategyController,
    ExecutivePitchModel,
    MarketOpportunityResult,
    evaluate_tam_sam_som_market_opportunity,
    audit_pitch_deck_structure,
    generate_singapore_grand_finale_playbook,
    EXACT_TAM_USD_B,
    EXACT_SAM_USD_B,
    EXACT_SOM_USD_M
)
from mcp_hub.hub import execute_tool_logic


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_phase_25_execution_invariant():
    """
    Verification Target: PRD Phase 25 Invariant Gate.
    Asserts ExecutivePitchModel schema validation and TAM/SAM/SOM market opportunity compliance.
    """
    controller = FinaleStrategyController()
    sample_payload = {
        "event_id": "TEST-PHASE-25",
        "tam_usd_b": 12.8,
        "sam_usd_b": 3.2,
        "som_usd_m": 480.0
    }
    result = await controller.execute_phase_pipeline(sample_payload)
    assert isinstance(result, ExecutivePitchModel)
    assert result.event_id == "TEST-PHASE-25"
    assert result.verified_flag is True
    assert result.metadata["status"] == "OPERATIONAL"
    assert result.metadata["phase_id"] == 25
    assert "market_evaluation" in result.metadata
    market_eval = result.metadata["market_evaluation"]
    assert market_eval["is_compliant"] is True
    assert market_eval["tam_usd_b"] == 12.8
    assert market_eval["sam_usd_b"] == 3.2
    assert market_eval["som_usd_m"] == 480.0
    assert market_eval["verdict"] == "PASSED_STRICT_TAM_SAM_SOM_GATE"


@pytest.mark.asyncio
async def test_phase_25_empty_payload_rejection():
    """Asserts that empty payload is rejected with ValueError."""
    controller = FinaleStrategyController()
    with pytest.raises(ValueError) as excinfo:
        await controller.execute_phase_pipeline({})
    assert "Empty payload rejected" in str(excinfo.value)


def test_mathematical_governing_equation_tam_sam_som():
    """
    Governing Equation Invariant:
        TAM = $12.8B, SAM = $3.2B, SOM = $480M ($0.48B)
        Bounds: SOM <= SAM <= TAM with strict positive bounds.
    """
    # Case 1: Exact target market sizing
    res1 = evaluate_tam_sam_som_market_opportunity(
        tam_usd_b=12.8,
        sam_usd_b=3.2,
        som_usd_m=480.0
    )
    assert res1.is_compliant is True
    assert res1.tam_usd_b == 12.8
    assert res1.sam_usd_b == 3.2
    assert res1.som_usd_m == 480.0
    assert res1.som_usd_b == 0.48
    assert res1.sam_pct_of_tam == 25.0
    assert res1.som_pct_of_sam == 15.0
    assert res1.verdict == "PASSED_STRICT_TAM_SAM_SOM_GATE"
    assert res1.status == "COMPLIANT"

    # Case 2: Hierarchy inversion (SOM > SAM)
    res2 = evaluate_tam_sam_som_market_opportunity(
        tam_usd_b=12.8,
        sam_usd_b=3.2,
        som_usd_m=4000.0  # $4.0B > $3.2B SAM
    )
    assert res2.is_compliant is False
    assert res2.verdict == "MARKET_HIERARCHY_INVERSION_ERROR"
    assert res2.status == "NON_COMPLIANT_HIERARCHY"

    # Case 3: Hierarchy inversion (SAM > TAM)
    res3 = evaluate_tam_sam_som_market_opportunity(
        tam_usd_b=10.0,
        sam_usd_b=15.0,  # $15B > $10B TAM
        som_usd_m=480.0
    )
    assert res3.is_compliant is False
    assert res3.verdict == "MARKET_HIERARCHY_INVERSION_ERROR"
    assert res3.status == "NON_COMPLIANT_HIERARCHY"

    # Case 4: Non-positive parameters
    res4 = evaluate_tam_sam_som_market_opportunity(
        tam_usd_b=-12.8,
        sam_usd_b=3.2,
        som_usd_m=480.0
    )
    assert res4.is_compliant is False
    assert res4.verdict == "NON_POSITIVE_MARKET_PARAMETERS_ERROR"

    # Case 5: TAM out of bounds (> 12.85B)
    res5 = evaluate_tam_sam_som_market_opportunity(
        tam_usd_b=18.0,
        sam_usd_b=3.2,
        som_usd_m=480.0
    )
    assert res5.is_compliant is False
    assert res5.verdict == "TAM_BOUNDS_VIOLATION_ERROR"
    assert res5.status == "NON_COMPLIANT_TAM"

    # Case 6: SAM out of bounds (> 3.25B)
    res6 = evaluate_tam_sam_som_market_opportunity(
        tam_usd_b=12.8,
        sam_usd_b=4.5,
        som_usd_m=480.0
    )
    assert res6.is_compliant is False
    assert res6.verdict == "SAM_BOUNDS_VIOLATION_ERROR"
    assert res6.status == "NON_COMPLIANT_SAM"

    # Case 7: SOM out of bounds (> 485M)
    res7 = evaluate_tam_sam_som_market_opportunity(
        tam_usd_b=12.8,
        sam_usd_b=3.2,
        som_usd_m=600.0
    )
    assert res7.is_compliant is False
    assert res7.verdict == "SOM_BOUNDS_VIOLATION_ERROR"
    assert res7.status == "NON_COMPLIANT_SOM"


def test_docs_pitch_deck_static_inspection():
    """
    Verifies that docs/PITCH_DECK.md exists, contains all 10 core topics,
    and covers critical Google Cloud and IEEE ClimateChain Global Demonstration keywords.
    """
    audit = audit_pitch_deck_structure()
    assert audit["file_exists"] is True
    assert audit["is_compliant"] is True
    assert audit["verdict"] == "PASSED_INVESTOR_DECK_AUDIT"
    assert audit["total_lines"] >= 100
    assert audit["word_count"] >= 1000
    assert audit["keywords_verified"]["Google Cloud Run"] is True
    assert audit["keywords_verified"]["Google Vertex AI"] is True
    assert audit["keywords_verified"]["Singapore"] is True


def test_singapore_grand_finale_playbook_spec():
    """
    Verifies the IEEE ClimateChain Global Demonstration 48-Hour Live Demo Execution Playbook.
    """
    playbook = generate_singapore_grand_finale_playbook()
    assert "Singapore" in playbook["venue"]
    demo_spec = playbook["live_demo_spec"]
    assert demo_spec["lat"] == 1.2800
    assert demo_spec["lon"] == 103.8636
    assert demo_spec["simulated_rainfall_mm"] == 150.0
    assert demo_spec["surge_height_m"] == 2.5
    assert demo_spec["pacing_seconds"] == 180

    arc = playbook["four_minute_pitch_arc"]
    assert len(arc) == 4
    assert "0:00 - 0:45" in arc[0]["window"]
    assert "3:00 - 4:00" in arc[3]["window"]

    ask = playbook["financial_ask"]
    assert ask["round"] == "Series Seed"
    assert ask["target_amount_usd"] == 2500000
    assert ask["pre_money_valuation_usd"] == 10000000


@pytest.mark.asyncio
async def test_circuit_breaker_failover_recovery():
    """
    Verifies 3-Tier Circuit Breaker behavior:
    3 consecutive failures trip state to OPEN -> triggers Tier 2 fallback response.
    """
    controller = FinaleStrategyController()
    assert controller.circuit_state == "CLOSED"

    # Trip breaker by recording 3 failures
    controller.record_failure()
    controller.record_failure()
    controller.record_failure()
    assert controller.circuit_state == "OPEN"

    # When OPEN, requests route to Tier 2 fallback model
    fallback_res = await controller.execute_phase_pipeline({"event_id": "TEST-BREAKER-P25"})
    assert fallback_res.execution_tier == "TIER2_FALLBACK"
    assert fallback_res.metadata["status"] == "CIRCUIT_BREAKER_ACTIVE_TIER2_FALLBACK"

    # Simulate cooldown expiration to HALF-OPEN
    controller.last_failure_time = time.time() - 35.0
    status_diag = controller.get_circuit_status()
    assert status_diag["state"] == "HALF-OPEN"

    # Reset on success
    controller.record_success()
    assert controller.circuit_state == "CLOSED"
    assert controller.failure_count == 0


def test_rest_api_strategy_endpoints(client):
    """
    Tests REST API endpoints mounted in backend/app/routes/strategy.py.
    """
    # 1. Health Endpoint
    res_health = client.get("/strategy/phase25/health")
    assert res_health.status_code == 200
    h_data = res_health.json()
    assert h_data["phase_id"] == 25
    assert h_data["status"] == "OPERATIONAL"
    assert "TAM = $12.8B" in h_data["governing_equation"]

    # 2. TAM Evaluate Endpoint
    payload = {
        "tam_usd_b": 12.8,
        "sam_usd_b": 3.2,
        "som_usd_m": 480.0
    }
    res_eval = client.post("/strategy/tam/evaluate", json=payload)
    assert res_eval.status_code == 200
    e_data = res_eval.json()
    assert e_data["is_compliant"] is True
    assert e_data["verdict"] == "PASSED_STRICT_TAM_SAM_SOM_GATE"

    # 3. Deck Audit Endpoint
    res_audit = client.get("/strategy/deck/audit")
    assert res_audit.status_code == 200
    a_data = res_audit.json()
    assert a_data["status"] == "success"
    assert a_data["audit"]["verdict"] == "PASSED_INVESTOR_DECK_AUDIT"

    # 4. Grand Finale Playbook Endpoint
    res_playbook = client.get("/strategy/grandfinale/playbook")
    assert res_playbook.status_code == 200
    p_data = res_playbook.json()
    assert p_data["status"] == "success"
    assert "Singapore" in p_data["playbook"]["venue"]

    # 5. Pipeline Endpoint
    pipe_payload = {"event_id": "API-TEST-P25", "tam_usd_b": 12.8, "sam_usd_b": 3.2, "som_usd_m": 480.0}
    res_pipe = client.post("/strategy/phase25/pipeline", json=pipe_payload)
    assert res_pipe.status_code == 200
    pipe_data = res_pipe.json()
    assert pipe_data["event_id"] == "API-TEST-P25"
    assert pipe_data["execution_tier"] == "ENTERPRISE_PROD"


def test_mcp_hub_phase25_tool_dispatch():
    """
    Tests MCP Hub tool execution for Phase 25 tools via execute_tool_logic.
    """
    # 1. evaluate_tam_sam_som_market_opportunity
    res_mkt = execute_tool_logic(
        "evaluate_tam_sam_som_market_opportunity",
        {"tam_usd_b": 12.8, "sam_usd_b": 3.2, "som_usd_m": 480.0}
    )
    assert res_mkt["is_compliant"] is True
    assert res_mkt["verdict"] == "PASSED_STRICT_TAM_SAM_SOM_GATE"

    # 2. audit_pitch_deck_slides
    res_audit = execute_tool_logic("audit_pitch_deck_slides", {})
    assert res_audit["is_compliant"] is True
    assert res_audit["verdict"] == "PASSED_INVESTOR_DECK_AUDIT"

    # 3. get_singapore_grand_finale_playbook
    res_playbook = execute_tool_logic("get_singapore_grand_finale_playbook", {})
    assert "Singapore" in res_playbook["venue"]
    assert res_playbook["financial_ask"]["target_amount_usd"] == 2500000
