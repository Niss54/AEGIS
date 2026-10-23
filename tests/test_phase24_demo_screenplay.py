"""
AEGIS-CLIMATE Phase 24 Verification Test Suite
IEEE ClimateChain 3-Minute Video Demo Screenplay & Teleprompter Plan
Governance: Gravitas Reliability Runtime · Mathematical Invariant Verification
"""
import os
import time
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.screenplay import (
    ScreenplayController,
    DemoScreenplayModel,
    ScreenplayTimingResult,
    evaluate_screenplay_timing_budget,
    parse_and_validate_demo_script,
    generate_teleprompter_cue_sheet,
    EXACT_TOTAL_DURATION_S
)
from mcp_hub.hub import execute_tool_logic


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_phase_24_execution_invariant():
    """
    Verification Target: PRD Phase 24 Invariant Gate.
    Asserts DemoScreenplayModel schema validation and Delta_t = 30s + 60s + 60s + 30s = 180s.
    """
    controller = ScreenplayController()
    sample_payload = {
        "event_id": "TEST-PHASE-24",
        "act1_crisis_s": 30.0,
        "act2_ui_s": 60.0,
        "act3_cloud_s": 60.0,
        "act4_roi_s": 30.0
    }
    result = await controller.execute_phase_pipeline(sample_payload)
    assert isinstance(result, DemoScreenplayModel)
    assert result.event_id == "TEST-PHASE-24"
    assert result.verified_flag is True
    assert result.metadata["status"] == "OPERATIONAL"
    assert result.metadata["phase_id"] == 24
    assert "timing_evaluation" in result.metadata
    timing_eval = result.metadata["timing_evaluation"]
    assert timing_eval["is_timing_compliant"] is True
    assert timing_eval["total_duration_s"] == 180.0
    assert timing_eval["verdict"] == "PASSED_STRICT_SCREENPLAY_TIMING_GATE"


@pytest.mark.asyncio
async def test_phase_24_empty_payload_rejection():
    """Asserts that empty payload is rejected with ValueError."""
    controller = ScreenplayController()
    with pytest.raises(ValueError) as excinfo:
        await controller.execute_phase_pipeline({})
    assert "Empty payload rejected" in str(excinfo.value)


def test_mathematical_governing_equation_screenplay_timing():
    """
    Governing Equation Invariant:
        Delta_t = 30s (Crisis) + 60s (UI) + 60s (Cloud) + 30s (ROI) = 180s
    """
    # Case 1: Exact target timing
    res1 = evaluate_screenplay_timing_budget(
        act1_crisis_s=30.0,
        act2_ui_s=60.0,
        act3_cloud_s=60.0,
        act4_roi_s=30.0
    )
    assert res1.is_timing_compliant is True
    assert res1.total_duration_s == 180.0
    assert res1.verdict == "PASSED_STRICT_SCREENPLAY_TIMING_GATE"
    assert res1.status == "COMPLIANT"

    # Case 2: Timing within tolerance (+/- 0.5s per act, 180.2s total)
    res2 = evaluate_screenplay_timing_budget(
        act1_crisis_s=29.8,
        act2_ui_s=60.2,
        act3_cloud_s=60.1,
        act4_roi_s=30.1
    )
    assert res2.is_timing_compliant is True
    assert res2.verdict == "PASSED_STRICT_SCREENPLAY_TIMING_GATE"

    # Case 3: Total duration mismatch (>181s)
    res3 = evaluate_screenplay_timing_budget(
        act1_crisis_s=30.0,
        act2_ui_s=60.0,
        act3_cloud_s=60.0,
        act4_roi_s=40.0
    )
    assert res3.is_timing_compliant is False
    assert res3.verdict == "TOTAL_DURATION_MISMATCH_ERROR"
    assert res3.status == "NON_COMPLIANT_DURATION"

    # Case 4: Act proportion imbalance (180s total but unequal ratio)
    res4 = evaluate_screenplay_timing_budget(
        act1_crisis_s=45.0,
        act2_ui_s=45.0,
        act3_cloud_s=45.0,
        act4_roi_s=45.0
    )
    assert res4.is_timing_compliant is False
    assert res4.verdict == "ACT_PROPORTION_IMBALANCE_ERROR"
    assert res4.status == "NON_COMPLIANT_ACT_RATIO"


def test_docs_demo_script_static_inspection():
    """
    Verifies that docs/DEMO_SCRIPT.md exists, contains all 4 Acts,
    and covers critical Google Cloud and IEEE ClimateChain Global Demonstration keywords.
    """
    audit = parse_and_validate_demo_script()
    assert audit["status"] == "AUDITED"
    assert audit["valid"] is True
    assert audit["all_acts_present"] is True
    assert audit["acts"]["act1_crisis"] is True
    assert audit["acts"]["act2_cockpit_ui"] is True
    assert audit["acts"]["act3_google_cloud"] is True
    assert audit["acts"]["act4_roi_singapore"] is True
    assert len(audit["missing_keywords"]) == 0
    assert audit["total_word_count"] > 200


def test_teleprompter_cue_sheet_generation():
    """
    Verifies teleprompter cue sheet formatting and duration continuity.
    """
    cues = generate_teleprompter_cue_sheet()
    assert cues["total_duration_seconds"] == EXACT_TOTAL_DURATION_S
    assert len(cues["cues"]) == 4

    durations = [c["duration_seconds"] for c in cues["cues"]]
    assert durations == [30.0, 60.0, 60.0, 30.0]
    assert sum(durations) == 180.0


def test_record_demo_assets_script():
    """
    Verifies that scripts/record_demo_assets.py exists in the repository.
    """
    script_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "record_demo_assets.py")
    assert os.path.exists(script_path), "scripts/record_demo_assets.py must exist"


@pytest.mark.asyncio
async def test_circuit_breaker_transitions():
    """
    Verifies 3-tier circuit breaker:
    CLOSED -> (3 failures) -> OPEN -> (cooldown) -> HALF_OPEN -> (success) -> CLOSED.
    """
    controller = ScreenplayController()
    controller.cooldown_period = 0.2  # 200ms
    assert controller.circuit_state == "CLOSED"

    # Simulate 3 consecutive failures
    controller._record_failure("Teleprompter streaming lag 1")
    controller._record_failure("Teleprompter streaming lag 2")
    assert controller.circuit_state == "CLOSED"
    controller._record_failure("Teleprompter streaming lag 3")
    assert controller.circuit_state == "OPEN"

    # In OPEN state, pipeline routes to fallback
    res_open = await controller.execute_phase_pipeline({
        "event_id": "TEST-SCREENPLAY-FALLBACK",
        "act1_crisis_s": 30.0
    })
    assert res_open.execution_tier == "LOCAL_FALLBACK"

    # Cooldown expires -> HALF_OPEN
    time.sleep(0.25)
    assert controller._evaluate_circuit_state() == "HALF_OPEN"

    # Successful request resets state to CLOSED
    controller._record_success()
    assert controller.circuit_state == "CLOSED"
    assert controller.failure_count == 0


def test_rest_screenplay_endpoints(client):
    """Verifies FastAPI REST endpoints under /screenplay and /api/v1/screenplay."""
    # 1. Health check
    resp_h = client.get("/screenplay/phase24/health")
    assert resp_h.status_code == 200
    data_h = resp_h.json()
    assert data_h["status"] == "healthy"
    assert data_h["phase"] == 24

    # 2. Pipeline execution
    resp_p = client.post("/screenplay/phase24/pipeline", json={
        "event_id": "TEST-REST-PHASE-24",
        "act1_crisis_s": 30.0,
        "act2_ui_s": 60.0,
        "act3_cloud_s": 60.0,
        "act4_roi_s": 30.0
    })
    assert resp_p.status_code == 200
    data_p = resp_p.json()
    assert data_p["event_id"] == "TEST-REST-PHASE-24"
    assert data_p["verified_flag"] is True

    # 3. Timing evaluation
    resp_t = client.post("/screenplay/timing/evaluate", json={
        "act1_crisis_s": 30.0,
        "act2_ui_s": 60.0,
        "act3_cloud_s": 60.0,
        "act4_roi_s": 30.0
    })
    assert resp_t.status_code == 200
    data_t = resp_t.json()
    assert data_t["is_timing_compliant"] is True
    assert data_t["verdict"] == "PASSED_STRICT_SCREENPLAY_TIMING_GATE"

    # 4. Script audit
    resp_a = client.get("/screenplay/script/audit")
    assert resp_a.status_code == 200
    assert resp_a.json()["valid"] is True
    assert resp_a.json()["all_acts_present"] is True

    # 5. Teleprompter cues
    resp_c = client.get("/screenplay/teleprompter/cues")
    assert resp_c.status_code == 200
    assert len(resp_c.json()["cues"]) == 4


def test_mcp_tools_execution():
    """Verifies Phase 24 MCP tools registered and dispatched correctly."""
    # 1. evaluate_screenplay_timing_budget
    res1 = execute_tool_logic("evaluate_screenplay_timing_budget", {
        "act1_crisis_s": 30.0,
        "act2_ui_s": 60.0,
        "act3_cloud_s": 60.0,
        "act4_roi_s": 30.0
    })
    assert res1["is_timing_compliant"] is True
    assert res1["verdict"] == "PASSED_STRICT_SCREENPLAY_TIMING_GATE"

    # 2. audit_demo_script_screenplay
    res2 = execute_tool_logic("audit_demo_script_screenplay", {})
    assert res2["valid"] is True
    assert res2["status"] == "AUDITED"

    # 3. get_teleprompter_cue_sheet
    res3 = execute_tool_logic("get_teleprompter_cue_sheet", {})
    assert res3["total_duration_seconds"] == 180.0
    assert len(res3["cues"]) == 4
