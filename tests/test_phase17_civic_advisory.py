"""
AEGIS-CLIMATE Phase 17 Verification Test Suite
Bilingual Civic Advisory Synthesis (English & Devanagari Hindi)
Governance: Gravitas Reliability Runtime · Mathematical Invariant Verification
"""
import time
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.civic_advisory import (
    CivicAdvisoryController,
    CivicAdvisoryModel,
    validate_and_clamp_advisory_bounds,
    generate_local_deterministic_advisory,
    synthesize_bilingual_advisory_sync
)
from mcp_hub.hub import execute_tool_logic


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_phase_17_execution_invariant():
    """
    Verification Target: PRD Phase 17 Invariant Gate.
    Asserts CivicAdvisoryModel schema validation and operational metadata.
    """
    controller = CivicAdvisoryController()
    sample_payload = {
        "event_id": "TEST-PHASE-17",
        "location": "Bengaluru Bellandur Catchment",
        "effective_precip_mm": 110.0,
        "waterlogging_depth_cm": 95,
        "buildings_at_risk": 412,
        "var_inr": 350000000.0
    }
    result = await controller.execute_phase_pipeline(sample_payload)
    assert isinstance(result, CivicAdvisoryModel)
    assert result.event_id == "TEST-PHASE-17"
    assert result.verified_flag is True
    assert result.metadata["status"] == "OPERATIONAL"
    assert result.metadata["phase_id"] == 17
    assert "data" in result.metadata
    assert result.metadata["data"]["location"] == "Bengaluru Bellandur Catchment"


@pytest.mark.asyncio
async def test_phase_17_empty_payload_rejection():
    """Asserts that empty payload is rejected with ValueError."""
    controller = CivicAdvisoryController()
    with pytest.raises(ValueError) as excinfo:
        await controller.execute_phase_pipeline({})
    assert "Empty payload rejected" in str(excinfo.value)


def test_mathematical_governing_equation_bounds_clamping():
    """
    Governing Equation Invariant:
    Inputs to Advisory_Devanagari = Gemini2.0(P_eff, D_water, Lang=hi)
    must satisfy physical bounds:
      0.0 <= P_eff <= 1000.0 mm
      0 <= D_water <= 500 cm
      0 <= B_risk <= 10000 structures
      0.0 <= VaR
    """
    # Test case 1: Standard realistic values (no clamping required)
    p, d, b, v, meta = validate_and_clamp_advisory_bounds(95.0, 85, 340, 250000000.0)
    assert p == 95.0
    assert d == 85
    assert b == 340
    assert v == 250000000.0
    assert meta["clamped_applied"] is False

    # Test case 2: Extreme values exceeding upper bounds
    p2, d2, b2, v2, meta2 = validate_and_clamp_advisory_bounds(2500.0, 750, 25000, 1000000.0)
    assert p2 == 1000.0
    assert d2 == 500
    assert b2 == 10000
    assert v2 == 1000000.0
    assert meta2["clamped_applied"] is True

    # Test case 3: Negative/out-of-bounds lower limits
    p3, d3, b3, v3, meta3 = validate_and_clamp_advisory_bounds(-50.0, -20, -100, -500.0)
    assert p3 == 0.0
    assert d3 == 0
    assert b3 == 0
    assert v3 == 0.0
    assert meta3["clamped_applied"] is True


@pytest.mark.asyncio
async def test_bilingual_advisory_devanagari_synthesis():
    """
    Verifies bilingual alert synthesis in English and natural Devanagari Hindi.
    """
    controller = CivicAdvisoryController()
    res = await controller.synthesize_bilingual_advisory(
        location="Mumbai Mithi River Basin",
        effective_precip_mm=95.0,
        waterlogging_depth_cm=85,
        buildings_at_risk=340,
        var_inr=250000000.0
    )
    assert res["status"] == "COMPLETED"
    assert res["location"] == "Mumbai Mithi River Basin"
    assert "EXECUTIVE" in res["english_advisory"]
    assert "आपातकालीन" in res["hindi_advisory"]
    assert "सेमी" in res["hindi_advisory"] or "जलभराव" in res["hindi_advisory"]
    assert res["latency_ms"] >= 0.0
    assert res["execution_tier"] in ("ENTERPRISE_PROD", "CROSS_CLOUD_FAILOVER", "LOCAL_FALLBACK")


@pytest.mark.asyncio
async def test_circuit_breaker_transitions():
    """
    Verifies 3-tier circuit breaker:
    CLOSED -> (3 failures) -> OPEN -> (cooldown) -> HALF_OPEN -> (success) -> CLOSED.
    """
    controller = CivicAdvisoryController()
    controller.cooldown_period = 0.2  # 200ms cooldown for fast test
    assert controller.circuit_state == "CLOSED"

    # 1. Simulate 3 consecutive failures
    controller._record_failure("Upstream timeout 1")
    controller._record_failure("Upstream timeout 2")
    assert controller.circuit_state == "CLOSED"
    controller._record_failure("Upstream timeout 3")
    assert controller.circuit_state == "OPEN"

    # 2. In OPEN state, routing should go directly to LOCAL_FALLBACK
    res_open = await controller.synthesize_bilingual_advisory(
        location="Assam Brahmaputra Basin",
        effective_precip_mm=140.0,
        waterlogging_depth_cm=110,
        buildings_at_risk=520,
        var_inr=420000000.0
    )
    assert res_open["execution_tier"] == "LOCAL_FALLBACK"
    assert res_open["model_used"] == "DeterministicBhashaAI"

    # 3. Wait for cooldown to expire -> HALF_OPEN
    time.sleep(0.25)
    assert controller._evaluate_circuit_state() == "HALF_OPEN"

    # 4. Successful execution closes circuit back to CLOSED
    controller._record_success()
    assert controller.circuit_state == "CLOSED"
    assert controller.failure_count == 0


def test_rest_civic_endpoints(client):
    """Verifies FastAPI REST endpoints under /civic and /api/v1/civic."""
    # 1. Health endpoint
    resp_h = client.get("/civic/phase17/health")
    assert resp_h.status_code == 200
    data_h = resp_h.json()
    assert data_h["status"] == "healthy"
    assert data_h["phase"] == 17

    # 2. Advisory generate endpoint
    gen_payload = {
        "location": "Chennai Ennore Thermal Zone",
        "effective_precip_mm": 125.0,
        "waterlogging_depth_cm": 90,
        "buildings_at_risk": 210,
        "var_inr": 180000000.0,
        "generate_speech": False
    }
    resp_gen = client.post("/civic/advisory/generate", json=gen_payload)
    assert resp_gen.status_code == 200
    data_gen = resp_gen.json()
    assert data_gen["status"] == "success"
    assert "english_advisory" in data_gen
    assert "hindi_advisory" in data_gen
    assert "आपातकालीन" in data_gen["hindi_advisory"]

    # 3. Pipeline endpoint
    resp_pipe = client.post("/civic/phase17/pipeline", json=gen_payload)
    assert resp_pipe.status_code == 200
    data_pipe = resp_pipe.json()
    assert data_pipe["verified_flag"] is True
    assert data_pipe["metadata"]["status"] == "OPERATIONAL"

    # 4. Speech endpoint
    speech_payload = {
        "text": "आपातकालीन चेतावनी: भारी बारिश की संभावना है।",
        "language": "hi",
        "speaker": "priya"
    }
    resp_sp = client.post("/civic/speech/synthesize", json=speech_payload)
    assert resp_sp.status_code == 200
    data_sp = resp_sp.json()
    assert "provider" in data_sp
    assert data_sp["language"] == "hi"


def test_mcp_civic_advisory_tools():
    """Verifies MCP JSON-RPC tool dispatches for Phase 17."""
    # 1. generate_bilingual_civic_advisory
    res1 = execute_tool_logic("generate_bilingual_civic_advisory", {
        "location": "Mundra Port Logistics SEZ",
        "effective_precip_mm": 80.0,
        "waterlogging_depth_cm": 60,
        "buildings_at_risk": 150,
        "var_inr": 120000000.0
    })
    assert res1["status"] == "COMPLETED"
    assert "Mundra Port Logistics SEZ" in res1["location"]
    assert "english_advisory" in res1
    assert "hindi_advisory" in res1

    # 2. validate_civic_advisory_bounds
    res2 = execute_tool_logic("validate_civic_advisory_bounds", {
        "effective_precip_mm": 1500.0,
        "waterlogging_depth_cm": 650,
        "buildings_at_risk": 20000,
        "var_inr": -100.0
    })
    assert res2["effective_precip_mm"] == 1000.0
    assert res2["waterlogging_depth_cm"] == 500
    assert res2["buildings_at_risk"] == 10000
    assert res2["var_inr"] == 0.0
    assert res2["bounds_metadata"]["clamped_applied"] is True

    # 3. synthesize_civic_speech
    res3 = execute_tool_logic("synthesize_civic_speech", {
        "text": "Emergency disaster briefing for civic protection.",
        "language": "en"
    })
    assert "provider" in res3
    assert res3["language"] == "en"
