"""
TERRA-SENTINEL Phase 23 Verification Test Suite
End-to-End Regression Verification & 52-Test Automated Quality Gate
Governance: Gravitas Reliability Runtime · Mathematical Invariant Verification
"""
import os
import time
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.quality_gate import (
    QualityGateController,
    TestGateModel,
    QualityGateResult,
    evaluate_quality_gate,
    discover_and_audit_test_suites,
    MIN_MANDATORY_PASSED_TESTS,
    MAX_PERMISSIBLE_FAILURES
)
from mcp_hub.hub import execute_tool_logic


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_phase_23_execution_invariant():
    """
    Verification Target: PRD Phase 23 Invariant Gate.
    Asserts TestGateModel schema validation and Passed >= 52 / 52 (100% Pass Rate), Failed = 0.
    """
    controller = QualityGateController()
    sample_payload = {
        "event_id": "TEST-PHASE-23",
        "passed_count": 62,
        "failed_count": 0,
        "skipped_count": 0
    }
    result = await controller.execute_phase_pipeline(sample_payload)
    assert isinstance(result, TestGateModel)
    assert result.event_id == "TEST-PHASE-23"
    assert result.verified_flag is True
    assert result.metadata["status"] == "OPERATIONAL"
    assert result.metadata["phase_id"] == 23
    assert "gate_evaluation" in result.metadata
    gate_eval = result.metadata["gate_evaluation"]
    assert gate_eval["is_gate_cleared"] is True
    assert gate_eval["verdict"] == "PASSED_STRICT_REGRESSION_GATE"
    assert gate_eval["pass_rate_pct"] == 100.0


@pytest.mark.asyncio
async def test_phase_23_empty_payload_rejection():
    """Asserts that empty payload is rejected with ValueError."""
    controller = QualityGateController()
    with pytest.raises(ValueError) as excinfo:
        await controller.execute_phase_pipeline({})
    assert "Empty payload rejected" in str(excinfo.value)


def test_mathematical_governing_equation_quality_gate():
    """
    Governing Equation Invariant:
        Passed >= 52 / 52 (100% Pass Rate), Failed = 0
    """
    # Case 1: Standard production regression clearance (62 passed, 0 failed)
    res1 = evaluate_quality_gate(passed_count=62, failed_count=0)
    assert res1.is_gate_cleared is True
    assert res1.pass_rate_pct == 100.0
    assert res1.verdict == "PASSED_STRICT_REGRESSION_GATE"
    assert res1.status == "COMPLIANT"

    # Case 2: Exact threshold boundary (52 passed, 0 failed)
    res2 = evaluate_quality_gate(passed_count=52, failed_count=0)
    assert res2.is_gate_cleared is True
    assert res2.pass_rate_pct == 100.0
    assert res2.verdict == "PASSED_STRICT_REGRESSION_GATE"

    # Case 3: Regression failure detected (60 passed, 2 failed)
    res3 = evaluate_quality_gate(passed_count=60, failed_count=2)
    assert res3.is_gate_cleared is False
    assert res3.verdict == "REGRESSION_FAILURES_DETECTED"
    assert res3.status == "FAILED_REGRESSION"

    # Case 4: Insufficient test volume (<52 passed)
    res4 = evaluate_quality_gate(passed_count=45, failed_count=0)
    assert res4.is_gate_cleared is False
    assert res4.verdict == "INSUFFICIENT_TEST_VOLUME_DEFICIT"
    assert res4.status == "INCOMPLETE_VERIFICATION"


def test_discover_and_audit_test_suites():
    """
    Verifies that the repository contains >= 20 test suites and meets the minimum 52 test functions.
    """
    audit = discover_and_audit_test_suites()
    assert audit["status"] == "AUDITED"
    assert audit["total_test_suites"] >= 20
    assert audit["total_test_functions"] >= MIN_MANDATORY_PASSED_TESTS
    assert audit["meets_minimum_volume"] is True
    assert len(audit["phase_coverage_map"]) >= 10


@pytest.mark.asyncio
async def test_circuit_breaker_transitions():
    """
    Verifies 3-tier circuit breaker:
    CLOSED -> (3 failures) -> OPEN -> (cooldown) -> HALF_OPEN -> (success) -> CLOSED.
    """
    controller = QualityGateController()
    controller.cooldown_period = 0.2  # 200ms
    assert controller.circuit_state == "CLOSED"

    # Simulate 3 consecutive failures
    controller._record_failure("Test runner process crash 1")
    controller._record_failure("Test runner process crash 2")
    assert controller.circuit_state == "CLOSED"
    controller._record_failure("Test runner process crash 3")
    assert controller.circuit_state == "OPEN"

    # In OPEN state, pipeline routes to fallback
    res_open = await controller.execute_phase_pipeline({
        "event_id": "TEST-QUALITY-FALLBACK",
        "passed_count": 52
    })
    assert res_open.execution_tier == "LOCAL_FALLBACK"

    # Cooldown expires -> HALF_OPEN
    time.sleep(0.25)
    assert controller._evaluate_circuit_state() == "HALF_OPEN"

    # Successful request resets state to CLOSED
    controller._record_success()
    assert controller.circuit_state == "CLOSED"
    assert controller.failure_count == 0


def test_rest_quality_endpoints(client):
    """Verifies FastAPI REST endpoints under /quality and /api/v1/quality."""
    # 1. Health check
    resp_h = client.get("/quality/phase23/health")
    assert resp_h.status_code == 200
    data_h = resp_h.json()
    assert data_h["status"] == "healthy"
    assert data_h["phase"] == 23

    # 2. Pipeline execution
    resp_p = client.post("/quality/phase23/pipeline", json={
        "event_id": "TEST-REST-PHASE-23",
        "passed_count": 62,
        "failed_count": 0,
        "skipped_count": 0
    })
    assert resp_p.status_code == 200
    data_p = resp_p.json()
    assert data_p["event_id"] == "TEST-REST-PHASE-23"
    assert data_p["verified_flag"] is True

    # 3. Gate evaluation
    resp_v = client.post("/quality/gate/evaluate", json={
        "passed_count": 55,
        "failed_count": 0,
        "skipped_count": 0
    })
    assert resp_v.status_code == 200
    data_v = resp_v.json()
    assert data_v["is_gate_cleared"] is True
    assert data_v["verdict"] == "PASSED_STRICT_REGRESSION_GATE"

    # 4. Audit suites
    resp_a = client.get("/quality/suites/audit")
    assert resp_a.status_code == 200
    assert resp_a.json()["status"] == "AUDITED"
    assert resp_a.json()["total_test_suites"] >= 20

    # 5. Quality summary
    resp_s = client.get("/quality/summary")
    assert resp_s.status_code == 200
    assert resp_s.json()["gate_status"] == "PASSED"


def test_mcp_tools_execution():
    """Verifies Phase 23 MCP tools registered and dispatched correctly."""
    # 1. evaluate_test_quality_gate
    res1 = execute_tool_logic("evaluate_test_quality_gate", {
        "passed_count": 62,
        "failed_count": 0
    })
    assert res1["is_gate_cleared"] is True
    assert res1["verdict"] == "PASSED_STRICT_REGRESSION_GATE"

    # 2. discover_test_suites_audit
    res2 = execute_tool_logic("discover_test_suites_audit", {})
    assert res2["status"] == "AUDITED"
    assert res2["total_test_suites"] >= 20

    # 3. get_quality_assurance_metrics
    res3 = execute_tool_logic("get_quality_assurance_metrics", {})
    assert res3["phase"] == 23
    assert res3["min_mandatory_passed"] == 52
