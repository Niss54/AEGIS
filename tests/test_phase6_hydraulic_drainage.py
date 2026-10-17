"""
Phase 6: Municipal Drainage Network & Verifiable Telemetry Verification Suite
Governance: Gravitas Reliability Runtime · Mathematical Invariant Adherence

Verifies:
1. D_water mathematical governing formula across boundary extremes.
2. HydraulicDrainageController execution pipeline and Pydantic V2 GeoContourModel contract.
3. Stormwater conduit network simulation and chokepoint detection.
4. FastAPI endpoints: /geo/hydraulic/simulate, /geo/hydraulic/conduits, /geo/hydraulic/pipeline.
5. MCP Hub JSON-RPC tool invocation for compute_hydraulic_flow_accumulation.
6. Zero-Trust HMAC-SHA256 sealing, tamper detection, and replay defense.
7. Bi-directional offline storage sync reconciliation.
"""
import pytest
import time
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.hydraulic import (
    hydraulic_controller,
    HydraulicDrainageController,
    HydraulicSimulationRequest
)
from backend.app.security import (
    telemetry_security_controller,
    TelemetryIntegrityController
)

client = TestClient(app)


def test_mathematical_governing_equation_invariants():
    """
    Validates formula: D_water = max(0, (P_eff - C_drain) / 10) * (1 + 1 / (1 + Slope))
    """
    # Invariant 1: When precipitation is below conduit capacity, net waterlogging is 0.0
    d_zero = HydraulicDrainageController.calculate_waterlogging_depth(
        precipitation_mm_hr=15.0,
        soil_saturation_pct=50.0,
        drainage_capacity_mm_hr=40.0,
        slope_gradient=0.03
    )
    assert d_zero == 0.0, f"Expected 0.0 cm depth for sub-capacity rain, got {d_zero}"

    # Invariant 2: Cloudburst scenario (200 mm/hr, 90% soil saturation, 35 mm/hr drainage)
    d_cloudburst_flat = HydraulicDrainageController.calculate_waterlogging_depth(
        precipitation_mm_hr=200.0,
        soil_saturation_pct=90.0,
        drainage_capacity_mm_hr=35.0,
        slope_gradient=0.01  # very flat
    )
    assert d_cloudburst_flat > 15.0, f"Expected severe waterlogging > 15cm, got {d_cloudburst_flat}"

    # Invariant 3: Steep slope reduces pooling depth compared to flat depression
    d_steep = HydraulicDrainageController.calculate_waterlogging_depth(
        precipitation_mm_hr=200.0,
        soil_saturation_pct=90.0,
        drainage_capacity_mm_hr=35.0,
        slope_gradient=0.25  # steep terrain
    )
    assert d_steep < d_cloudburst_flat, f"Steep slope ({d_steep}) must have less pooling than flat ({d_cloudburst_flat})"


@pytest.mark.asyncio
async def test_phase_6_execution_invariant_prd_contract():
    """
    Validates PRD.md Section 16 Phase 6 execution invariant contract.
    """
    controller = HydraulicDrainageController()
    sample_payload = {
        "event_id": "TEST-PHASE-6-INVARIANT",
        "precipitation_mm_hr": 120.0,
        "soil_saturation_pct": 85.0,
        "drainage_capacity_mm_hr": 35.0,
        "slope_gradient": 0.02
    }
    result = await controller.execute_phase_pipeline(sample_payload)
    assert result.event_id == "TEST-PHASE-6-INVARIANT"
    assert result.verified_flag is True
    assert result.metadata["status"] == "OPERATIONAL"
    assert result.metadata["phase_id"] == 6
    assert result.metadata["waterlogging_depth_cm"] > 0.0
    assert result.metadata["conduit_count"] == 4


def test_hydraulic_simulate_endpoint():
    """
    Tests POST /api/v1/geo/hydraulic/simulate endpoint.
    """
    payload = {
        "lat": 19.0760,
        "lon": 72.8777,
        "precipitation_mm_hr": 110.0,
        "soil_saturation_pct": 82.0,
        "drainage_capacity_mm_hr": 35.0,
        "slope_gradient": 0.02,
        "catchment_area_km2": 15.0
    }
    response = client.post("/api/v1/geo/hydraulic/simulate", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "event_id" in data
    assert data["waterlogging_depth_cm"] > 0
    assert data["drainage_surcharge_pct"] > 100.0  # 110mm / 35mm > 300%
    assert data["hydraulic_risk_tier"] in ("INFRASTRUCTURE_FAILURE", "HIGH_SURCHARGE")
    assert len(data["conduit_network"]) == 4
    assert data["flow_vectors_geojson"]["type"] == "FeatureCollection"


def test_hydraulic_conduits_endpoint():
    """
    Tests GET /api/v1/geo/hydraulic/conduits/{event_id} endpoint.
    """
    response = client.get("/api/v1/geo/hydraulic/conduits/EVT-TEST-001?precipitation_mm_hr=95.0")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["event_id"] == "EVT-TEST-001"
    assert data["conduit_count"] == 4
    assert any(c["choke_status"] in ("SURCHARGED", "CRITICAL_BLOCKED", "WARNING") for c in data["conduits"])


def test_mcp_hydraulic_tool_invocation():
    """
    Tests MCP Hub dispatcher invocation for compute_hydraulic_flow_accumulation tool.
    """
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "compute_hydraulic_flow_accumulation",
            "arguments": {
                "precipitation_mm_hr": 140.0,
                "drainage_capacity_mm_hr": 35.0,
                "soil_saturation_pct": 85.0,
                "slope_gradient": 0.02
            }
        },
        "id": "test-mcp-phase6"
    }
    response = client.post("/mcp/invoke", json=payload)
    assert response.status_code == 200, response.text
    res = response.json()
    assert "result" in res
    data = res["result"].get("data", res["result"])
    assert data["tool"] == "compute_hydraulic_flow_accumulation"
    assert data["waterlogging_depth_cm"] > 0.0
    assert data["conduit_count"] == 4


def test_zero_trust_telemetry_sealing_and_verification():
    """
    Tests HMAC-SHA256 cryptographic sealing and tamper-free verification.
    """
    sensor_data = {
        "precipitation_mm_hr": 88.5,
        "soil_moisture_pct": 79.2,
        "water_head_cm": 42.0
    }
    seal_res = client.post("/api/v1/telemetry/seal", json={
        "station_id": "STN-MUMBAI-04",
        "lat": 19.0760,
        "lon": 72.8777,
        "telemetry": sensor_data
    })
    assert seal_res.status_code == 200, seal_res.text
    seal = seal_res.json()
    assert seal["status"] == "CRYPTOGRAPHICALLY_SEALED"
    assert len(seal["hmac_sha256_signature"]) == 64  # valid SHA-256 hex string

    # Verify legitimate payload
    verify_res = client.post("/api/v1/telemetry/verify", json={
        "event_id": seal["event_id"],
        "station_id": seal["station_id"],
        "timestamp_epoch": seal["timestamp_epoch"],
        "nonce": seal["nonce"],
        "payload": {
            "station_id": seal["station_id"],
            "lat": 19.0760,
            "lon": 72.8777,
            "telemetry": sensor_data
        },
        "signature": seal["hmac_sha256_signature"]
    })
    assert verify_res.status_code == 200
    verify_data = verify_res.json()
    assert verify_data["is_valid"] is True
    assert verify_data["integrity_status"] == "VERIFIED_TAMPER_FREE"


def test_zero_trust_tamper_detection():
    """
    Tests that altered sensor values in transit are cryptographically caught and rejected.
    """
    sensor_data = {"precipitation_mm_hr": 88.5, "water_head_cm": 42.0}
    seal_res = client.post("/api/v1/telemetry/seal", json={
        "station_id": "STN-MUMBAI-05",
        "lat": 19.0760,
        "lon": 72.8777,
        "telemetry": sensor_data
    })
    seal = seal_res.json()

    # Adversary alters rainfall reading from 88.5 to 10.0 (fraudulent claim)
    tampered_payload = {
        "station_id": seal["station_id"],
        "lat": 19.0760,
        "lon": 72.8777,
        "telemetry": {"precipitation_mm_hr": 10.0, "water_head_cm": 42.0}
    }
    verify_res = client.post("/api/v1/telemetry/verify", json={
        "event_id": seal["event_id"],
        "station_id": seal["station_id"],
        "timestamp_epoch": seal["timestamp_epoch"],
        "nonce": "different-nonce-1234",
        "payload": tampered_payload,
        "signature": seal["hmac_sha256_signature"]
    })
    verify_data = verify_res.json()
    assert verify_data["is_valid"] is False
    assert "mismatch" in verify_data["rejection_reason"] or "tampered" in verify_data["rejection_reason"]
    assert verify_data["integrity_status"] == "INTEGRITY_VIOLATION_DETECTED"


def test_anti_replay_attack_defense():
    """
    Tests that reusing the same nonce is rejected as a replay attack.
    """
    sensor_data = {"rain": 50.0}
    seal = telemetry_security_controller.generate_seal("STN-REPLAY-01", sensor_data)

    # First verification passes
    valid, reason, _ = telemetry_security_controller.verify_seal(
        station_id="STN-REPLAY-01",
        payload=sensor_data,
        signature=seal["hmac_sha256_signature"],
        timestamp=seal["timestamp_epoch"],
        nonce=seal["nonce"]
    )
    assert valid is True

    # Replay with same nonce must be denied
    valid_replay, reason_replay, _ = telemetry_security_controller.verify_seal(
        station_id="STN-REPLAY-01",
        payload=sensor_data,
        signature=seal["hmac_sha256_signature"],
        timestamp=seal["timestamp_epoch"],
        nonce=seal["nonce"]
    )
    assert valid_replay is False
    assert "Replay attack detected" in str(reason_replay)


def test_multi_tier_offline_sync():
    """
    Tests offline local queue reconciliation via POST /api/v1/sync/offline-batch.
    """
    batch = {
        "device_id": "EDGE-FIELD-OFFICER-TABLET-09",
        "synced_at_epoch": time.time(),
        "records": [
            {
                "client_record_id": "LOCAL-REC-001",
                "entity_type": "incident_report",
                "created_at_epoch": time.time() - 3600,
                "payload": {"severity": "CRITICAL", "water_depth_cm": 95, "location": "Kurla West"}
            },
            {
                "client_record_id": "LOCAL-REC-002",
                "entity_type": "sensor_telemetry",
                "created_at_epoch": time.time() - 1800,
                "payload": {"station": "STN-LOCAL-01", "rain_mm": 130.5}
            }
        ]
    }
    response = client.post("/api/v1/sync/offline-batch", json=batch)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["total_received"] == 2
    assert data["total_processed"] == 2
    assert len(data["reconciliation_log"]) == 2
    assert all(r["status"] in ("RECONCILED", "MERGED") for r in data["reconciliation_log"])

    # Test status endpoint
    status_res = client.get("/api/v1/sync/status")
    assert status_res.status_code == 200
    assert status_res.json()["state"] == "OPERATIONAL"
    assert status_res.json()["total_records_synchronized"] >= 2
