"""
TERRA-SENTINEL Phase 19 Verification Test Suite
Edge Network Resilience: Service Worker & Local Storage Fallback
Governance: Gravitas Reliability Runtime · Mathematical Invariant Verification
"""
import os
import time
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.edge_worker import (
    EdgeWorkerController,
    PWAWorkerModel,
    evaluate_edge_availability,
    reconcile_offline_queue
)
from mcp_hub.hub import execute_tool_logic


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_phase_19_execution_invariant():
    """
    Verification Target: PRD Phase 19 Invariant Gate.
    Asserts PWAWorkerModel schema validation, 100% availability tracking, and operational metadata.
    """
    controller = EdgeWorkerController()
    sample_payload = {
        "event_id": "TEST-PHASE-19",
        "is_online": True,
        "has_cached_shell": True,
        "has_local_heuristics": True
    }
    result = await controller.execute_phase_pipeline(sample_payload)
    assert isinstance(result, PWAWorkerModel)
    assert result.event_id == "TEST-PHASE-19"
    assert result.verified_flag is True
    assert result.metadata["status"] == "OPERATIONAL"
    assert result.metadata["phase_id"] == 19
    assert "availability_evaluation" in result.metadata
    avail_eval = result.metadata["availability_evaluation"]
    assert avail_eval["is_100pct_available"] is True
    assert avail_eval["availability_percentage"] == 100.0


@pytest.mark.asyncio
async def test_phase_19_empty_payload_rejection():
    """Asserts that empty payload is rejected with ValueError."""
    controller = EdgeWorkerController()
    with pytest.raises(ValueError) as excinfo:
        await controller.execute_phase_pipeline({})
    assert "Empty payload rejected" in str(excinfo.value)


def test_mathematical_governing_equation_edge_availability():
    """
    Governing Equation Invariant:
        Availability = 100% (Cached Shell ⊕ Local Heuristics)
    """
    # Case 1: Normal online connectivity
    res1 = evaluate_edge_availability(is_online=True, has_cached_shell=True, has_local_heuristics=True)
    assert res1.is_100pct_available is True
    assert res1.availability_percentage == 100.0
    assert res1.operational_mode == "CLOUD_CONNECTED_ENTERPRISE"

    # Case 2: Catastrophic infrastructure blackout (is_online = False)
    # 100% availability preserved via Cached Shell ⊕ Local Heuristics
    res2 = evaluate_edge_availability(is_online=False, has_cached_shell=True, has_local_heuristics=True)
    assert res2.is_100pct_available is True
    assert res2.availability_percentage == 100.0
    assert res2.operational_mode == "OFFLINE_RESILIENT_SURVIVAL"

    # Case 3: Partition without cached shell
    res3 = evaluate_edge_availability(is_online=False, has_cached_shell=False, has_local_heuristics=True)
    assert res3.is_100pct_available is False
    assert res3.availability_percentage == 0.0
    assert res3.operational_mode == "DEGRADED_PARTITION"


def test_pwa_service_worker_asset_spec():
    """
    Verifies that frontend/public/sw.js exists and contains core shell caching assets.
    """
    sw_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "sw.js")
    assert os.path.exists(sw_path), "frontend/public/sw.js must exist for PWA offline operation"
    with open(sw_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "terra-sentinel-v1.0.0" in content
    assert "STATIC_ASSETS" in content
    assert "OFFLINE_RESILIENT_SURVIVAL" in content


@pytest.mark.asyncio
async def test_circuit_breaker_transitions():
    """
    Verifies 3-tier circuit breaker:
    CLOSED -> (3 failures) -> OPEN -> (cooldown) -> HALF_OPEN -> (success) -> CLOSED.
    """
    controller = EdgeWorkerController()
    controller.cooldown_period = 0.2  # 200ms
    assert controller.circuit_state == "CLOSED"

    # Simulate 3 consecutive failures
    controller._record_failure("PWA registration partition 1")
    controller._record_failure("PWA registration partition 2")
    assert controller.circuit_state == "CLOSED"
    controller._record_failure("PWA registration partition 3")
    assert controller.circuit_state == "OPEN"

    # In OPEN state, pipeline routes to fallback
    res_open = await controller.execute_phase_pipeline({
        "event_id": "TEST-PWA-FALLBACK",
        "is_online": False
    })
    assert res_open.execution_tier == "LOCAL_FALLBACK"

    # Cooldown expires -> HALF_OPEN
    time.sleep(0.25)
    assert controller._evaluate_circuit_state() == "HALF_OPEN"

    # Successful request resets state to CLOSED
    controller._record_success()
    assert controller.circuit_state == "CLOSED"
    assert controller.failure_count == 0


def test_rest_edge_endpoints(client):
    """Verifies FastAPI REST endpoints under /edge and /api/v1/edge."""
    # 1. Health check
    resp_h = client.get("/edge/phase19/health")
    assert resp_h.status_code == 200
    data_h = resp_h.json()
    assert data_h["status"] == "healthy"
    assert data_h["phase"] == 19

    # 2. Availability evaluation endpoint
    eval_payload = {
        "is_online": False,
        "has_cached_shell": True,
        "has_local_heuristics": True
    }
    resp_eval = client.post("/edge/availability/evaluate", json=eval_payload)
    assert resp_eval.status_code == 200
    data_eval = resp_eval.json()
    assert data_eval["is_100pct_available"] is True
    assert data_eval["availability_percentage"] == 100.0

    # 3. Pipeline endpoint
    resp_pipe = client.post("/edge/phase19/pipeline", json=eval_payload)
    assert resp_pipe.status_code == 200
    data_pipe = resp_pipe.json()
    assert data_pipe["verified_flag"] is True
    assert data_pipe["metadata"]["status"] == "OPERATIONAL"

    # 4. Offline reconciliation endpoint
    recon_payload = {
        "mutations": [
            {"id": "MUT-1", "endpoint": "/api/v1/tools/predict", "payload": {"soil": 85.0}}
        ]
    }
    resp_recon = client.post("/edge/reconcile", json=recon_payload)
    assert resp_recon.status_code == 200
    data_recon = resp_recon.json()
    assert data_recon["status"] == "RECONCILED"
    assert data_recon["processed_count"] == 1

    # 5. Manifest endpoint
    resp_man = client.get("/edge/manifest")
    assert resp_man.status_code == 200
    data_man = resp_man.json()
    assert "TERRA-SENTINEL" in data_man["name"]
    assert data_man["display"] == "standalone"


def test_mcp_edge_tools():
    """Verifies MCP JSON-RPC tool dispatches for Phase 19."""
    # 1. evaluate_edge_offline_availability
    res1 = execute_tool_logic("evaluate_edge_offline_availability", {
        "is_online": False,
        "has_cached_shell": True,
        "has_local_heuristics": True
    })
    assert res1["is_100pct_available"] is True
    assert res1["availability_percentage"] == 100.0

    # 2. get_pwa_edge_manifest
    res2 = execute_tool_logic("get_pwa_edge_manifest", {})
    assert res2["status"] == "OPERATIONAL"
    assert "ServiceWorker_Asset_Cache" in res2["offline_capabilities"]

    # 3. reconcile_edge_offline_queue
    res3 = execute_tool_logic("reconcile_edge_offline_queue", {
        "mutations": [{"id": "M1"}, {"id": "M2"}]
    })
    assert res3["status"] == "RECONCILED"
    assert res3["processed_count"] == 2
