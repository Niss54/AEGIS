"""
AEGIS-CLIMATE Production Verification: Phase 12
Suite: Multi-Tier Storage Architecture & Bi-Directional Offline Sync
Governance: Gravitas Reliability Runtime · Machine-Checked Evidence Protocol
"""
import pytest
import time
from fastapi.testclient import TestClient

from backend.app.main import app as backend_app
from backend.app.storage_sync import StorageSyncController, OfflineSyncModel
from mcp_hub.hub import app as hub_app


@pytest.fixture
def controller():
    return StorageSyncController()


@pytest.fixture
def client():
    return TestClient(backend_app)


@pytest.fixture
def mcp_client():
    return TestClient(hub_app)


# ============================================================================
# 1. PRD Invariant & Pipeline Execution Tests
# ============================================================================

@pytest.mark.asyncio
async def test_phase_12_execution_invariant(controller):
    """
    PRD Invariant Test: Verifies OfflineSyncModel generation and operational metadata.
    """
    sample_payload = {
        "event_id": "TEST-PHASE-12",
        "device_id": "FIELD-TABLET-01",
        "client_state": {"asset-1": {"status": "normal"}},
        "records": [
            {"client_record_id": "rec-1", "created_at_epoch": time.time(), "entity_type": "sensor_telemetry", "payload": {"rain": 50}}
        ]
    }
    result = await controller.execute_phase_pipeline(sample_payload)

    assert isinstance(result, OfflineSyncModel)
    assert result.event_id == "TEST-PHASE-12"
    assert result.verified_flag is True
    assert result.execution_tier == "ENTERPRISE_PROD"
    assert result.metadata["status"] == "OPERATIONAL"
    assert result.metadata["phase_id"] == 12
    assert result.metadata["reconcile_summary"]["is_consistent"] is True
    assert result.metadata["reconcile_summary"]["records_processed"] == 1


@pytest.mark.asyncio
async def test_phase_12_empty_payload_rejection(controller):
    """
    PRD Boundary Test: Empty payload must be strictly rejected.
    """
    with pytest.raises(ValueError, match="Empty payload rejected"):
        await controller.execute_phase_pipeline({})


# ============================================================================
# 2. Mathematical Governing Equation: State_Client ⊕ Delta_Offline ≡ State_Cloud
# ============================================================================

def test_mathematical_governing_equation_deterministic_reconciliation(controller):
    """
    Validates formula: State_Client ⊕ Delta_Offline ≡ State_Cloud
    Ensures deterministic, timestamp-ordered delta application.
    """
    base_client_state = {
        "sensor-A": {"created_at_epoch": 1000.0, "value": 10, "label": "base"},
        "sensor-B": {"created_at_epoch": 1000.0, "value": 20, "label": "base"}
    }

    # Offline mutations occurred during network partition
    offline_delta = [
        {"client_record_id": "sensor-A", "created_at_epoch": 1050.0, "value": 15, "label": "offline_update"},
        {"client_record_id": "sensor-C", "created_at_epoch": 1060.0, "value": 30, "label": "offline_new"}
    ]

    target_cloud = controller.apply_delta(base_client_state, offline_delta)

    # Invariant checks:
    # 1. sensor-A was updated via newer timestamp (1050 > 1000)
    assert target_cloud["sensor-A"]["value"] == 15
    assert target_cloud["sensor-A"]["sync_status"] == "MERGED_LWW"

    # 2. sensor-B remained untouched
    assert target_cloud["sensor-B"]["value"] == 20

    # 3. sensor-C was inserted as new record
    assert target_cloud["sensor-C"]["value"] == 30
    assert target_cloud["sensor-C"]["sync_status"] == "COMMITTED_NEW"


def test_last_write_wins_conflict_resolution(controller):
    """
    Verifies that if cloud has a newer timestamp than an offline record,
    the cloud record is preserved and not overwritten by stale client data.
    """
    base_state = {
        "sensor-X": {"created_at_epoch": 2000.0, "value": 99, "source": "cloud"}
    }
    stale_offline_delta = [
        {"client_record_id": "sensor-X", "created_at_epoch": 1900.0, "value": 12, "source": "stale_client"}
    ]

    result = controller.apply_delta(base_state, stale_offline_delta)
    # Value must remain 99 because 2000.0 > 1900.0
    assert result["sensor-X"]["value"] == 99
    assert result["sensor-X"]["sync_status"] == "CONFLICT_RETAINED_CLOUD"


def test_multi_tier_l1_l2_storage_sync(controller):
    """
    Verifies that reconciliation updates both L1 fast cache and L2 persistent datastore.
    """
    assert len(controller.l1_cache) == 0
    assert len(controller.l2_datastore) == 0

    delta = [
        {"client_record_id": "poi-1", "created_at_epoch": 100.0, "location": "Dharavi"},
        {"client_record_id": "poi-2", "created_at_epoch": 105.0, "location": "Kurla"}
    ]
    reconciled = controller.reconcile("DEV-TEST-01", {}, delta)

    assert reconciled["is_consistent"] is True
    assert reconciled["records_processed"] == 2
    assert len(controller.l1_cache) == 2
    assert len(controller.l2_datastore) == 2
    assert controller.l1_cache["poi-1"]["location"] == "Dharavi"
    assert controller.l2_datastore["poi-2"]["location"] == "Kurla"


# ============================================================================
# 3. REST API Gateway Endpoints
# ============================================================================

def test_api_offline_batch_sync(client):
    """Verifies POST /api/v1/sync/offline-batch processes queued records."""
    req = {
        "device_id": "TABLET-MUMBAI-04",
        "synced_at_epoch": time.time(),
        "records": [
            {
                "client_record_id": f"rec-{int(time.time())}-1",
                "entity_type": "sensor_telemetry",
                "created_at_epoch": time.time() - 30.0,
                "payload": {"rainfall_mm": 88.0, "submerged_depth_cm": 40.0}
            }
        ]
    }
    resp = client.post("/api/v1/sync/offline-batch", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_received"] == 1
    assert data["total_processed"] == 1
    assert data["reconciliation_log"][0]["status"] in ("RECONCILED", "MERGED")


def test_api_sync_reconcile_endpoint(client):
    """Verifies POST /api/v1/sync/reconcile executes State_Client ⊕ Delta_Offline ≡ State_Cloud."""
    payload = {
        "device_id": "DEV-HTTP-RECON",
        "client_state": {"node-1": {"created_at_epoch": 100, "temp": 28}},
        "records": [{"client_record_id": "node-1", "created_at_epoch": 110, "temp": 31}]
    }
    resp = client.post("/api/v1/sync/reconcile", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_consistent"] is True
    assert data["reconciled_state"]["node-1"]["temp"] == 31


def test_api_sync_status(client):
    """Verifies GET /api/v1/sync/status reports multi-tier operational health."""
    resp = client.get("/api/v1/sync/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["state"] == "OPERATIONAL"
    assert data["cloud_database_connectivity"] == "CONNECTED"
    assert "sensor_telemetry" in data["supported_entities"]


def test_api_sync_pipeline(client):
    """Verifies POST /api/v1/sync/pipeline returns OfflineSyncModel."""
    payload = {
        "event_id": "TEST-REST-SYNC-PIPE",
        "device_id": "DRONE-CONTROLLER-01",
        "records": []
    }
    resp = client.post("/api/v1/sync/pipeline", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["event_id"] == "TEST-REST-SYNC-PIPE"
    assert data["verified_flag"] is True
    assert data["metadata"]["status"] == "OPERATIONAL"


# ============================================================================
# 4. Model Context Protocol (MCP) Tool Integration
# ============================================================================

def test_mcp_sync_offline_mutations_tool(mcp_client):
    """Verifies MCP Hub /mcp/invoke executes sync_offline_mutations tool."""
    rpc_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "sync_offline_mutations",
            "arguments": {
                "device_id": "DEV-MCP-SYNC",
                "client_state": {"valve-1": {"status": "closed", "created_at_epoch": 50}},
                "records": [
                    {"client_record_id": "valve-1", "status": "opened", "created_at_epoch": 60}
                ]
            }
        },
        "id": "mcp-sync-1"
    }
    resp = mcp_client.post("/mcp/invoke", json=rpc_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "mcp-sync-1"
    assert "result" in data
    assert data["result"]["isError"] is False
    assert data["result"]["data"]["is_consistent"] is True
    assert data["result"]["data"]["reconciled_state"]["valve-1"]["status"] == "opened"
