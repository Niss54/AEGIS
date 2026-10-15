"""
TERRA-SENTINEL Phase 22 Verification Test Suite
Vercel Edge Global Frontend Deployment & CDN Orchestration
Governance: Gravitas Reliability Runtime · Mathematical Invariant Verification
"""
import os
import time
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.vercel_edge import (
    VercelEdgeController,
    VercelEdgeModel,
    EdgePerformanceBudgetResult,
    evaluate_edge_performance_budget,
    inspect_vercel_configuration,
    get_edge_cdn_routing_spec,
    MAX_TTFB_MS,
    MIN_LIGHTHOUSE_SCORE
)
from mcp_hub.hub import execute_tool_logic


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_phase_22_execution_invariant():
    """
    Verification Target: PRD Phase 22 Invariant Gate.
    Asserts VercelEdgeModel schema validation and TTFB_global <= 80ms, LighthouseScore >= 98.
    """
    controller = VercelEdgeController()
    sample_payload = {
        "event_id": "TEST-PHASE-22",
        "ttfb_ms": 42.0,
        "lighthouse_score": 99,
        "edge_region": "bom1"
    }
    result = await controller.execute_phase_pipeline(sample_payload)
    assert isinstance(result, VercelEdgeModel)
    assert result.event_id == "TEST-PHASE-22"
    assert result.verified_flag is True
    assert result.metadata["status"] == "OPERATIONAL"
    assert result.metadata["phase_id"] == 22
    assert "edge_budget_evaluation" in result.metadata
    budget_eval = result.metadata["edge_budget_evaluation"]
    assert budget_eval["ttfb_compliant"] is True
    assert budget_eval["lighthouse_compliant"] is True
    assert budget_eval["performance_verdict"] == "PASSED_EDGE_PERFORMANCE_GATE"


@pytest.mark.asyncio
async def test_phase_22_empty_payload_rejection():
    """Asserts that empty payload is rejected with ValueError."""
    controller = VercelEdgeController()
    with pytest.raises(ValueError) as excinfo:
        await controller.execute_phase_pipeline({})
    assert "Empty payload rejected" in str(excinfo.value)


def test_mathematical_governing_equation_edge_performance():
    """
    Governing Equation Invariant:
        TTFB_global <= 80ms, LighthouseScore >= 98
    """
    # Case 1: Standard compliant edge delivery (Mumbai PoP)
    res1 = evaluate_edge_performance_budget(ttfb_ms=42.0, lighthouse_score=99, edge_region="bom1")
    assert res1.ttfb_compliant is True
    assert res1.lighthouse_compliant is True
    assert res1.performance_verdict == "PASSED_EDGE_PERFORMANCE_GATE"
    assert res1.compliance_status == "COMPLIANT"

    # Case 2: Exact boundary limits (80ms TTFB, 98 Lighthouse)
    res2 = evaluate_edge_performance_budget(ttfb_ms=80.0, lighthouse_score=98, edge_region="sin1")
    assert res2.ttfb_compliant is True
    assert res2.lighthouse_compliant is True
    assert res2.performance_verdict == "PASSED_EDGE_PERFORMANCE_GATE"

    # Case 3: TTFB latency violation (>80ms)
    res3 = evaluate_edge_performance_budget(ttfb_ms=92.5, lighthouse_score=99, edge_region="fra1")
    assert res3.ttfb_compliant is False
    assert res3.lighthouse_compliant is True
    assert res3.performance_verdict == "TTFB_LATENCY_VIOLATION"
    assert res3.compliance_status == "NON_COMPLIANT_LATENCY"

    # Case 4: Lighthouse audit deficit (<98)
    res4 = evaluate_edge_performance_budget(ttfb_ms=45.0, lighthouse_score=94, edge_region="bom1")
    assert res4.ttfb_compliant is True
    assert res4.lighthouse_compliant is False
    assert res4.performance_verdict == "LIGHTHOUSE_AUDIT_DEFICIT"
    assert res4.compliance_status == "NON_COMPLIANT_AUDIT"

    # Case 5: Double violation (latency exceeded and audit deficit)
    res5 = evaluate_edge_performance_budget(ttfb_ms=115.0, lighthouse_score=89, edge_region="iad1")
    assert res5.ttfb_compliant is False
    assert res5.lighthouse_compliant is False
    assert res5.performance_verdict == "DOUBLE_VIOLATION_DEFICIT"


def test_vercel_json_static_inspection():
    """
    Verifies that vercel.json defines reverse proxy rewrites,
    immutable caching, and HSTS security headers.
    """
    inspection = inspect_vercel_configuration()
    assert inspection["status"] == "VALIDATED"
    assert inspection["is_compliant"] is True
    assert inspection["has_api_v1_rewrite"] is True
    assert inspection["has_spa_fallback"] is True
    assert inspection["has_immutable_asset_cache"] is True
    assert inspection["has_hsts_security"] is True
    assert inspection["has_nosniff_header"] is True


def test_vite_config_optimization():
    """
    Verifies that frontend/vite.config.ts implements code splitting (manualChunks)
    and production build minification.
    """
    root_dir = os.path.join(os.path.dirname(__file__), "..")
    vite_cfg_path = os.path.join(root_dir, "frontend", "vite.config.ts")
    assert os.path.exists(vite_cfg_path), "frontend/vite.config.ts must exist"

    with open(vite_cfg_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "manualChunks" in content
    assert "vendor-react" in content
    assert "vendor-leaflet" in content
    assert "minify" in content


def test_edge_cdn_routing_spec():
    """
    Verifies Anycast Edge CDN point-of-presence topology.
    """
    spec = get_edge_cdn_routing_spec()
    assert "HTTP/3" in spec["protocol"]
    pops = [p["pop"] for p in spec["primary_pops"]]
    assert "bom1" in pops
    assert "sin1" in pops
    assert "iad1" in pops
    assert spec["invariants"]["max_ttfb_ms"] == 80.0
    assert spec["invariants"]["min_lighthouse_score"] == 98


@pytest.mark.asyncio
async def test_circuit_breaker_transitions():
    """
    Verifies 3-tier circuit breaker:
    CLOSED -> (3 failures) -> OPEN -> (cooldown) -> HALF_OPEN -> (success) -> CLOSED.
    """
    controller = VercelEdgeController()
    controller.cooldown_period = 0.2  # 200ms
    assert controller.circuit_state == "CLOSED"

    # Simulate 3 consecutive failures
    controller._record_failure("Vercel Edge deploy timeout 1")
    controller._record_failure("Vercel Edge deploy timeout 2")
    assert controller.circuit_state == "CLOSED"
    controller._record_failure("Vercel Edge deploy timeout 3")
    assert controller.circuit_state == "OPEN"

    # In OPEN state, pipeline routes to fallback
    res_open = await controller.execute_phase_pipeline({
        "event_id": "TEST-EDGE-FALLBACK",
        "ttfb_ms": 70.0
    })
    assert res_open.execution_tier == "LOCAL_FALLBACK"

    # Cooldown expires -> HALF_OPEN
    time.sleep(0.25)
    assert controller._evaluate_circuit_state() == "HALF_OPEN"

    # Successful request resets state to CLOSED
    controller._record_success()
    assert controller.circuit_state == "CLOSED"
    assert controller.failure_count == 0


def test_rest_vercel_endpoints(client):
    """Verifies FastAPI REST endpoints under /vercel and /api/v1/vercel."""
    # 1. Health check
    resp_h = client.get("/vercel/phase22/health")
    assert resp_h.status_code == 200
    data_h = resp_h.json()
    assert data_h["status"] == "healthy"
    assert data_h["phase"] == 22

    # 2. Pipeline execution
    resp_p = client.post("/vercel/phase22/pipeline", json={
        "event_id": "TEST-REST-PHASE-22",
        "ttfb_ms": 40.0,
        "lighthouse_score": 99,
        "edge_region": "bom1"
    })
    assert resp_p.status_code == 200
    data_p = resp_p.json()
    assert data_p["event_id"] == "TEST-REST-PHASE-22"
    assert data_p["verified_flag"] is True

    # 3. Performance evaluation
    resp_v = client.post("/vercel/performance/evaluate", json={
        "ttfb_ms": 38.5,
        "lighthouse_score": 99,
        "edge_region": "bom1"
    })
    assert resp_v.status_code == 200
    data_v = resp_v.json()
    assert data_v["ttfb_compliant"] is True
    assert data_v["lighthouse_compliant"] is True
    assert data_v["performance_verdict"] == "PASSED_EDGE_PERFORMANCE_GATE"

    # 4. Config inspect
    resp_c = client.get("/vercel/config/inspect")
    assert resp_c.status_code == 200
    assert resp_c.json()["is_compliant"] is True

    # 5. CDN routing
    resp_r = client.get("/vercel/cdn/routing")
    assert resp_r.status_code == 200
    assert "primary_pops" in resp_r.json()


def test_mcp_tools_execution():
    """Verifies Phase 22 MCP tools registered and dispatched correctly."""
    # 1. evaluate_edge_performance_budget
    res1 = execute_tool_logic("evaluate_edge_performance_budget", {
        "ttfb_ms": 45.0,
        "lighthouse_score": 99,
        "edge_region": "bom1"
    })
    assert res1["ttfb_compliant"] is True
    assert res1["performance_verdict"] == "PASSED_EDGE_PERFORMANCE_GATE"

    # 2. inspect_vercel_edge_configuration
    res2 = execute_tool_logic("inspect_vercel_edge_configuration", {})
    assert res2["is_compliant"] is True
    assert res2["has_immutable_asset_cache"] is True

    # 3. get_edge_cdn_routing_matrix
    res3 = execute_tool_logic("get_edge_cdn_routing_matrix", {})
    assert "primary_pops" in res3
    assert len(res3["primary_pops"]) >= 5
