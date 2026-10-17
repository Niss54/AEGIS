"""
Phase 27.3: Automated Test Suite for ClusterDuck Protocol LoRa Ad-Hoc Mesh Gateway
Derived from ClusterDuck-Protocol/ClusterDuck-Protocol
"""

import time
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.cluster_duck import cluster_duck_engine, ClusterDuckEngine, DuckPacket

client = TestClient(app)


def test_ingest_valid_duck_packet():
    """Verify standard LoRa DuckPacket ingestion, hop counting, and delivery calculation."""
    muid = f"test_muid_{int(time.time() * 1000)}"
    packet = {
        "sduid": "DUCK-SENS-01",
        "dduid": "PAPADUCK",
        "muid": muid,
        "topic": 3,  # WATER_LEVEL
        "path": ["DUCK-SENS-01", "MAMA-RELAY-02", "PAPA-GATEWAY-01"],
        "hop_count": 2,
        "max_hops": 6,
        "rssi": -76.0,
        "snr": 8.5,
        "payload": {
            "water_level_cm": 52.4,
            "battery_pct": 89.0
        }
    }
    response = client.post("/api/v1/telemetry/duckpacket", json=packet)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "INGESTED_SUCCESS"
    assert data["muid"] == muid
    assert data["delivered"] is True
    assert data["is_duplicate"] is False
    assert data["hop_count"] == 2
    assert data["delivery_probability"] > 0.70


def test_packet_deduplication_invariant():
    """Verify that multiple deliveries of the same MUID are dropped to prevent mesh flooding."""
    muid = f"dedup_test_{int(time.time() * 1000)}"
    packet = {
        "sduid": "DUCK-SENS-02",
        "dduid": "PAPADUCK",
        "muid": muid,
        "topic": 5,
        "path": ["DUCK-SENS-02", "MAMA-RELAY-01", "PAPA-GATEWAY-01"],
        "hop_count": 2,
        "max_hops": 6,
        "rssi": -80.0,
        "snr": 6.0,
        "payload": {"rain_gauge_mm": 18.0}
    }

    # First transmission: Success
    resp1 = client.post("/api/v1/telemetry/duckpacket", json=packet)
    assert resp1.status_code == 200
    assert resp1.json()["delivered"] is True

    # Duplicate transmission via alternate mesh hop: Dropped
    packet["path"] = ["DUCK-SENS-02", "MAMA-RELAY-02", "MAMA-RELAY-01", "PAPA-GATEWAY-01"]
    packet["hop_count"] = 3
    resp2 = client.post("/api/v1/telemetry/duckpacket", json=packet)
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "DUPLICATE_DROPPED"
    assert resp2.json()["is_duplicate"] is True
    assert resp2.json()["delivered"] is False


def test_max_hops_loop_prevention_invariant():
    """Verify packet is dropped when hop count exceeds max_hops (H > MaxHops)."""
    muid = f"loop_test_{int(time.time() * 1000)}"
    packet = {
        "sduid": "DUCK-LOOP-01",
        "dduid": "PAPADUCK",
        "muid": muid,
        "topic": 1,
        "path": ["N1", "N2", "N3", "N4", "N5", "N6", "N7"],
        "hop_count": 7,
        "max_hops": 6,
        "rssi": -92.0,
        "snr": 3.0,
        "payload": {"status": "looping"}
    }
    response = client.post("/api/v1/telemetry/duckpacket", json=packet)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "MAX_HOPS_EXCEEDED"
    assert data["delivered"] is False


def test_mesh_network_topology():
    """Verify mesh topology contains nodes (DuckLink, MamaDuck, PapaDuck), links, and stats."""
    response = client.get("/api/v1/mesh/topology")
    assert response.status_code == 200
    data = response.json()

    assert "nodes" in data
    assert "links" in data
    assert data["total_active_nodes"] >= 4
    assert data["average_mesh_delivery_rate"] >= 80.0
    assert "ONLINE" in data["gateway_status"]

    # Verify presence of all 3 node tiers
    types = [n["duck_type"] for n in data["nodes"]]
    assert "DuckLink" in types
    assert "MamaDuck" in types
    assert "PapaDuck" in types


def test_single_node_diagnostics():
    """Verify single node retrieval and 404 for unknown node."""
    resp = client.get("/api/v1/mesh/nodes/DUCK-SENS-01")
    assert resp.status_code == 200
    data = resp.json()
    assert data["duck_id"] == "DUCK-SENS-01"
    assert data["battery_pct"] > 0.0

    resp404 = client.get("/api/v1/mesh/nodes/DUCK-NONEXISTENT-99")
    assert resp404.status_code == 404


def test_emergency_sos_simulation():
    """Verify high-priority off-grid emergency SOS simulation."""
    sos_payload = {
        "origin_duck_id": "DUCK-FLOOD-ISOLATED-01",
        "location_name": "Kurla Central Rail Lowlands",
        "lat": 19.0650,
        "lon": 72.8810,
        "water_level_cm": 160.0,
        "civilians_trapped": 24,
        "urgency": "IMMEDIATE_AIRLIFT"
    }
    response = client.post("/api/v1/mesh/simulate-sos", json=sos_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "INGESTED_SUCCESS"
    assert data["sos_triggered"] is True

    # Verify node status updated to SOS_ALERT in topology
    topo_resp = client.get("/api/v1/mesh/topology")
    assert topo_resp.status_code == 200
    topo_data = topo_resp.json()
    assert topo_data["active_sos_alerts"] >= 1

    # Check simulated node exists
    sos_node = next((n for n in topo_data["nodes"] if n["duck_id"] == "DUCK-FLOOD-ISOLATED-01"), None)
    assert sos_node is not None
    assert sos_node["status"] == "SOS_ALERT"
    assert sos_node["water_level_cm"] == 160.0


def test_cluster_duck_circuit_breaker_resilience():
    """Verify circuit breaker trips to OPEN and delivers safe gateway-buffered response."""
    test_engine = ClusterDuckEngine()
    test_engine.consecutive_failures = 3
    test_engine.circuit_state = "OPEN"
    test_engine.last_failure_time = time.time()  # active cooldown

    packet = DuckPacket(
        sduid="DUCK-TEST-01",
        dduid="PAPADUCK",
        muid="cb_test_muid_01",
        topic=3,
        path=["DUCK-TEST-01", "PAPADUCK"],
        hop_count=1,
        max_hops=6,
        rssi=-80.0,
        snr=7.0,
        payload={"water_cm": 30.0}
    )

    res = test_engine.ingest_duck_packet(packet)
    assert res.status == "GATEWAY_BUFFERED_FALLBACK"
    assert res.delivered is True


def test_pipeline_diagnostics_and_health():
    """Verify telemetry diagnostics and health check endpoints."""
    resp_pipe = client.get("/api/v1/mesh/pipeline")
    assert resp_pipe.status_code == 200
    data = resp_pipe.json()
    assert data["status"] == "operational"
    assert "mesh_metrics" in data
    assert "protocols" in data

    resp_health = client.get("/api/v1/mesh/health")
    assert resp_health.status_code == 200
    assert resp_health.json()["status"] == "operational"
