"""
AEGIS-CLIMATE Phase 15 Automated Test Suite
Module: tests/test_phase15_parametric_bond.py
Governance: Gravitas Reliability Runtime · Machine-Checked Verification

Governing Mathematical Equation:
Trigger(D) = I_{D >= D_threshold} => Payout(Beneficiary)
"""

import pytest
import time
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.parametric_insurance import (
    evaluate_parametric_trigger,
    compute_settlement_receipt_hash,
    parametric_bond_controller,
    ParametricBondController,
    DisasterBondModel
)
from mcp_hub.hub import execute_tool_logic, JsonRpcRequest, invoke_tool


@pytest.fixture
def fresh_controller():
    return ParametricBondController()


def test_evaluate_parametric_trigger_invariant():
    """
    Verifies mathematical invariant:
    Trigger(D) = I_{D >= D_threshold} => Payout(Beneficiary)
    """
    # 1. Breach case: Depth 70cm >= Threshold 50cm
    res_breach = evaluate_parametric_trigger(
        depth_cm=70.0,
        threshold_cm=50.0,
        risk_score_bps=7500,
        principal_usd=100000.0,
        coverage_limit_usd=250000.0
    )
    assert res_breach["indicator"] == 1
    assert res_breach["triggered"] is True
    assert res_breach["depth_triggered"] is True
    assert res_breach["payout_amount_usd"] > 0.0
    assert res_breach["payout_amount_usd"] <= 250000.0
    assert "Trigger(D) = I_{D >= D_threshold} => Payout(Beneficiary)" in res_breach["governing_equation"]

    # 2. Sub-threshold case: Depth 25cm < 50cm, Risk 4000 < 6500
    res_safe = evaluate_parametric_trigger(
        depth_cm=25.0,
        threshold_cm=50.0,
        risk_score_bps=4000,
        threshold_risk_bps=6500,
        principal_usd=100000.0
    )
    assert res_safe["indicator"] == 0
    assert res_safe["triggered"] is False
    assert res_safe["payout_amount_usd"] == 0.0
    assert res_safe["severity_ratio"] == 0.0


def test_settlement_receipt_hash_determinism():
    """
    Verifies cryptographic determinism of settlement receipt hashes.
    """
    h1 = compute_settlement_receipt_hash("BOND-1", "ASSESS-1", 75000.0, "0xABCDEF")
    h2 = compute_settlement_receipt_hash("BOND-1", "ASSESS-1", 75000.0, "0xabcdef")
    assert h1 == h2
    assert h1.startswith("0x")
    assert len(h1) == 66


@pytest.mark.asyncio
async def test_parametric_bond_controller_settle(fresh_controller):
    """
    Verifies automated bond settlement execution and audit recording.
    """
    res = await fresh_controller.settle_parametric_bond(
        bond_id="BOND-MUMBAI-01",
        assessment_id="ASSESS-TS-001",
        depth_cm=65.0,
        risk_score_bps=8000,
        beneficiary="0x71C2E696688b14AE0D78278fCeB78C2651F87bF9"
    )
    assert res["status"] == "SETTLED_ONCHAIN"
    assert res["settlement_tier"] == "TIER_1_POLYGON_AMOY"
    assert res["payout_amount_usd"] > 0
    assert len(fresh_controller._local_settlement_ledger) == 1


@pytest.mark.asyncio
async def test_circuit_breaker_trip_and_cooldown(fresh_controller):
    """
    Verifies 3-tier circuit breaker:
    3 failures -> OPEN -> Tier 2 local fallback -> 30s cooldown -> HALF_OPEN probe -> reset to CLOSED.
    """
    assert fresh_controller.circuit_state == "CLOSED"

    # Force 3 failures
    for _ in range(3):
        await fresh_controller.settle_parametric_bond(
            bond_id="BOND-FAIL",
            assessment_id="ASSESS-FAIL",
            depth_cm=60.0,
            risk_score_bps=7500,
            beneficiary="0xFAIL",
            force_fallback=True
        )

    # State must be OPEN
    assert fresh_controller.circuit_state == "OPEN"
    health = fresh_controller.get_health()
    assert health["circuit_state"] == "OPEN"
    assert health["status"] == "DEGRADED_FALLBACK"

    # An execution during OPEN routes to TIER_2_LOCAL_FALLBACK
    fallback_res = await fresh_controller.settle_parametric_bond(
        bond_id="BOND-TEST",
        assessment_id="ASSESS-TEST",
        depth_cm=60.0,
        risk_score_bps=7500,
        beneficiary="0xRECIPIENT",
        force_fallback=False
    )
    assert fallback_res["settlement_tier"] == "TIER_2_LOCAL_FALLBACK"

    # Simulate 31 seconds cooldown elapsed
    fresh_controller.last_failure_time = time.time() - 31.0
    state_after_cooldown = fresh_controller._check_circuit()
    assert state_after_cooldown == "HALF_OPEN"

    # Success probe resets circuit to CLOSED
    probe_res = await fresh_controller.settle_parametric_bond(
        bond_id="BOND-PROBE",
        assessment_id="ASSESS-PROBE",
        depth_cm=60.0,
        risk_score_bps=7500,
        beneficiary="0xPROBE",
        force_fallback=False
    )
    assert probe_res["settlement_tier"] == "TIER_1_POLYGON_AMOY"
    assert fresh_controller.circuit_state == "CLOSED"


@pytest.mark.asyncio
async def test_cfmc_mitigation_reward_rule(fresh_controller):
    """
    Verifies Carbon Flood Mitigation Credit condition:
    risk >= 6500 (CRITICAL) and dem_depth < 20cm -> eligible for 100 CFMC.
    """
    # 1. Eligible event
    res_eligible = await fresh_controller.evaluate_cfmc_mitigation_reward(
        beneficiary="0xGREEN_MUNICIPALITY",
        assessment_id="ASSESS-CFMC-1",
        risk_score_bps=7500,
        dem_depth_cm=14.5
    )
    assert res_eligible["eligible"] is True
    assert res_eligible["reward_amount_cfmc"] == 100.0
    assert res_eligible["tx_hash"] is not None

    # 2. Ineligible event: flood depth not low enough (45cm >= 20cm)
    res_flooded = await fresh_controller.evaluate_cfmc_mitigation_reward(
        beneficiary="0xGREEN_MUNICIPALITY",
        assessment_id="ASSESS-CFMC-2",
        risk_score_bps=7500,
        dem_depth_cm=45.0
    )
    assert res_flooded["eligible"] is False
    assert res_flooded["reward_amount_cfmc"] == 0.0


def test_blockchain_phase15_api_endpoints():
    """
    Tests REST API endpoints for Phase 15.
    """
    client = TestClient(app)

    # 1. Evaluate trigger endpoint
    eval_resp = client.post("/api/v2/blockchain/parametric/evaluate", json={
        "waterlogging_depth_cm": 62.5,
        "threshold_depth_cm": 50.0,
        "risk_score_bps": 7200,
        "threshold_risk_bps": 6500,
        "notional_principal_usd": 150000.0,
        "coverage_limit_usd": 300000.0,
        "beneficiary": "0x71C2E696688b14AE0D78278fCeB78C2651F87bF9"
    })
    assert eval_resp.status_code == 200
    eval_data = eval_resp.json()
    assert eval_data["triggered"] is True
    assert eval_data["payout_amount_usd"] > 0

    # 2. Settle bond endpoint
    settle_resp = client.post("/api/v2/blockchain/parametric/settle", json={
        "bond_id": "BOND-REST-01",
        "assessment_id": "ASSESS-REST-01",
        "waterlogging_depth_cm": 62.5,
        "risk_score_bps": 7200,
        "beneficiary": "0x71C2E696688b14AE0D78278fCeB78C2651F87bF9",
        "force_fallback": False
    })
    assert settle_resp.status_code == 200
    settle_data = settle_resp.json()
    assert "settlement_id" in settle_data

    # 3. CFMC reward endpoint
    cfmc_resp = client.post("/api/v2/blockchain/parametric/cfmc/evaluate", json={
        "beneficiary": "0x71C2E696688b14AE0D78278fCeB78C2651F87bF9",
        "assessment_id": "ASSESS-REST-01",
        "risk_score_bps": 7200,
        "dem_depth_cm": 15.0,
        "lat": 19.0728,
        "lon": 72.8797
    })
    assert cfmc_resp.status_code == 200
    assert cfmc_resp.json()["eligible"] is True

    # 4. Health endpoint
    health_resp = client.get("/api/v2/blockchain/phase15/health")
    assert health_resp.status_code == 200
    assert health_resp.json()["phase"] == 15


def test_mcp_hub_phase15_tools():
    """
    Tests MCP Hub tool execution for Phase 15 tools.
    """
    # 1. evaluate_parametric_trigger
    eval_res = execute_tool_logic("evaluate_parametric_trigger", {
        "depth_cm": 55.0,
        "threshold_cm": 50.0,
        "risk_score_bps": 7200
    })
    assert eval_res["triggered"] is True

    # 2. settle_parametric_bond
    settle_res = execute_tool_logic("settle_parametric_bond", {
        "bond_id": "BOND-MCP-01",
        "assessment_id": "ASSESS-MCP-01",
        "depth_cm": 55.0,
        "risk_score_bps": 7200,
        "beneficiary": "0x71C2E696688b14AE0D78278fCeB78C2651F87bF9"
    })
    assert "settlement_id" in settle_res

    # 3. evaluate_cfmc_mitigation_reward
    cfmc_res = execute_tool_logic("evaluate_cfmc_mitigation_reward", {
        "beneficiary": "0x71C2E696688b14AE0D78278fCeB78C2651F87bF9",
        "assessment_id": "ASSESS-MCP-01",
        "risk_score_bps": 7000,
        "dem_depth_cm": 12.0
    })
    assert cfmc_res["eligible"] is True
    assert cfmc_res["reward_amount_cfmc"] == 100.0


@pytest.mark.asyncio
async def test_phase15_pipeline_prd_invariant():
    """
    Verifies PRD Section 4 & 6 execute_phase_pipeline invariant:
    result.verified_flag is True, result.metadata['status'] == 'OPERATIONAL'
    """
    controller = ParametricBondController()
    sample_payload = {"event_id": "TEST-PHASE-15", "telemetry": 55.0, "risk_score_bps": 7500}
    result = await controller.execute_phase_pipeline(sample_payload)
    assert isinstance(result, DisasterBondModel)
    assert result.event_id == "TEST-PHASE-15"
    assert result.verified_flag is True
    assert result.metadata["status"] == "OPERATIONAL"
    assert result.metadata["trigger_evaluation"]["triggered"] is True
