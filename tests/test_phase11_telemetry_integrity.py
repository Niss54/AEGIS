"""
AEGIS-CLIMATE Production Verification: Phase 11
Suite: Zero-Trust Verifiable Telemetry & Cryptographic HMAC Sealing
Governance: Gravitas Reliability Runtime · Machine-Checked Evidence Protocol
"""
import pytest
import time
import hashlib
import hmac
from fastapi.testclient import TestClient

from backend.app.main import app as backend_app
from backend.app.security import (
    TelemetryIntegrityController,
    VerifiableTelemetryModel,
    telemetry_security_controller
)
from mcp_hub.hub import app as hub_app


@pytest.fixture
def controller():
    return TelemetryIntegrityController()


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
async def test_phase_11_execution_invariant(controller):
    """
    PRD Invariant Test: Verifies VerifiableTelemetryModel generation and operational metadata.
    """
    sample_payload = {"event_id": "TEST-PHASE-11", "telemetry": 42.0, "station_id": "MUMBAI-STN-01"}
    result = await controller.execute_phase_pipeline(sample_payload)

    assert isinstance(result, VerifiableTelemetryModel)
    assert result.event_id == "TEST-PHASE-11"
    assert result.verified_flag is True
    assert result.execution_tier == "ENTERPRISE_PROD"
    assert result.metadata["status"] == "OPERATIONAL"
    assert "seal" in result.metadata
    assert "hmac_sha256_signature" in result.metadata["seal"]


@pytest.mark.asyncio
async def test_phase_11_empty_payload_rejection(controller):
    """
    PRD Boundary Test: Empty payload must be strictly rejected.
    """
    with pytest.raises(ValueError, match="Empty payload rejected"):
        await controller.execute_phase_pipeline({})


# ============================================================================
# 2. Mathematical Governing Equation & Deterministic Canonicalization
# ============================================================================

def test_mathematical_hmac_sha256_canonicalization(controller):
    """
    Validates formula: Sig = HMAC-SHA256(K_sensor, Payload || Timestamp || Nonce)
    And deterministic JSON canonicalization regardless of dictionary key insertion order.
    """
    payload_a = {"precipitation_mm": 120.5, "station": "STN-A", "humidity": 88}
    payload_b = {"station": "STN-A", "humidity": 88, "precipitation_mm": 120.5}

    canonical_a = controller.canonicalize(payload_a)
    canonical_b = controller.canonicalize(payload_b)
    assert canonical_a == canonical_b == '{"humidity":88,"precipitation_mm":120.5,"station":"STN-A"}'

    ts = 1776000000.0
    nonce = "abcd1234efgh5678"
    key = "secret-key-1234"

    seal_a = controller.generate_seal("STN-A", payload_a, secret_key=key, timestamp=ts, nonce=nonce)
    seal_b = controller.generate_seal("STN-A", payload_b, secret_key=key, timestamp=ts, nonce=nonce)

    assert seal_a["hmac_sha256_signature"] == seal_b["hmac_sha256_signature"]
    assert seal_a["nonce"] == nonce
    assert seal_a["timestamp_epoch"] == ts


# ============================================================================
# 3. Cryptographic Verification & Tamper Detection
# ============================================================================

def test_tamper_detection_on_telemetry_payload(controller):
    """
    Verifies that altering even a single byte in the telemetry payload
    immediately invalidates the signature and is flagged as a tamper event.
    """
    station = "STN-MITHI-02"
    key = "hardened-salt-key"
    ts = time.time()
    nonce = f"nonce-{time.perf_counter()}"

    original_payload = {"water_level_m": 4.5, "rainfall_24h_mm": 180.0}
    seal = controller.generate_seal(station, original_payload, secret_key=key, timestamp=ts, nonce=nonce)

    # 1. Untampered verification succeeds
    is_valid, reason, _ = controller.verify_seal(
        station, original_payload, seal["hmac_sha256_signature"], ts, nonce, secret_key=key
    )
    assert is_valid is True
    assert reason is None

    # 2. Tampered payload (sensor data artificially lowered by attacker)
    tampered_payload = {"water_level_m": 2.0, "rainfall_24h_mm": 180.0}
    fresh_nonce = f"fresh-{time.perf_counter()}"
    is_valid_tampered, reason_tampered, _ = controller.verify_seal(
        station, tampered_payload, seal["hmac_sha256_signature"], ts, fresh_nonce, secret_key=key
    )
    assert is_valid_tampered is False
    assert "mismatch" in reason_tampered or "tampered" in reason_tampered


def test_invalid_key_rejection(controller):
    """Verifies that an unauthorized secret key is rejected."""
    station = "STN-KURLA-01"
    ts = time.time()
    nonce = f"key-nonce-{time.perf_counter()}"
    payload = {"flow_rate_m3s": 55.0}

    seal = controller.generate_seal(station, payload, secret_key="correct-key", timestamp=ts, nonce=nonce)
    is_valid, reason, _ = controller.verify_seal(
        station, payload, seal["hmac_sha256_signature"], ts, nonce, secret_key="wrong-key"
    )
    assert is_valid is False
    assert "mismatch" in reason or "invalid" in reason


# ============================================================================
# 4. Anti-Replay Defense & Clock Drift Bounds
# ============================================================================

def test_anti_replay_defense(controller):
    """
    Verifies that a re-submitted telemetry nonce is flagged as a replay attack.
    """
    station = "STN-DHARAVI-05"
    key = "replay-test-key"
    ts = time.time()
    nonce = f"replay-nonce-{time.perf_counter()}"
    payload = {"submerged_depth_cm": 30.0}

    seal = controller.generate_seal(station, payload, secret_key=key, timestamp=ts, nonce=nonce)

    # First attempt: verified & valid
    valid_first, _, _ = controller.verify_seal(station, payload, seal["hmac_sha256_signature"], ts, nonce, secret_key=key)
    assert valid_first is True

    # Second attempt with same nonce: REJECTED as replay attack
    valid_second, reason, _ = controller.verify_seal(station, payload, seal["hmac_sha256_signature"], ts, nonce, secret_key=key)
    assert valid_second is False
    assert "Replay attack detected" in reason


def test_clock_drift_bounds_enforcement(controller):
    """
    Verifies that packets with timestamp drift > 300s are rejected.
    """
    station = "STN-BANDRA-09"
    key = "drift-key"
    nonce = f"drift-nonce-{time.perf_counter()}"
    payload = {"temp_c": 29.5}

    # Stale timestamp (400 seconds in past)
    stale_ts = time.time() - 400.0
    seal = controller.generate_seal(station, payload, secret_key=key, timestamp=stale_ts, nonce=nonce)

    is_valid, reason, drift = controller.verify_seal(
        station, payload, seal["hmac_sha256_signature"], stale_ts, nonce, secret_key=key
    )
    assert is_valid is False
    assert "Timestamp drift" in reason
    assert drift > 300.0


# ============================================================================
# 5. REST API Gateway Endpoints
# ============================================================================

def test_api_telemetry_seal_and_verify(client):
    """
    Verifies POST /api/v1/telemetry/seal and POST /api/v1/telemetry/verify end-to-end.
    """
    seal_req = {
        "station_id": "STN-INTEG-01",
        "lat": 19.0728,
        "lon": 72.8797,
        "telemetry": {"precipitation_24h_mm": 110.0, "soil_saturation_pct": 82.5}
    }
    seal_resp = client.post("/api/v1/telemetry/seal", json=seal_req)
    assert seal_resp.status_code == 200
    seal_data = seal_resp.json()
    assert seal_data["status"] == "CRYPTOGRAPHICALLY_SEALED"
    assert len(seal_data["hmac_sha256_signature"]) == 64

    # Verify endpoint
    verify_req = {
        "event_id": seal_data["event_id"],
        "station_id": seal_data["station_id"],
        "timestamp_epoch": seal_data["timestamp_epoch"],
        "nonce": seal_data["nonce"],
        "payload": {
            "station_id": seal_req["station_id"],
            "lat": seal_req["lat"],
            "lon": seal_req["lon"],
            "telemetry": seal_req["telemetry"]
        },
        "signature": seal_data["hmac_sha256_signature"]
    }
    verify_resp = client.post("/api/v1/telemetry/verify", json=verify_req)
    assert verify_resp.status_code == 200
    verify_data = verify_resp.json()
    assert verify_data["is_valid"] is True
    assert verify_data["integrity_status"] == "VERIFIED_TAMPER_FREE"


def test_api_telemetry_security_spec(client):
    """Verifies GET /api/v1/telemetry/security-spec reports enterprise audit standards."""
    resp = client.get("/api/v1/telemetry/security-spec")
    assert resp.status_code == 200
    data = resp.json()
    assert data["mac_algorithm"] == "HMAC-SHA256 (RFC 2104)"
    assert "FIPS 198-1" in data["standard_adherence"]


def test_api_telemetry_pipeline(client):
    """Verifies POST /api/v1/telemetry/pipeline returns VerifiableTelemetryModel."""
    payload = {"event_id": "TEST-REST-TELEM-PIPE", "station_id": "STN-PIPE-01", "humidity": 75}
    resp = client.post("/api/v1/telemetry/pipeline", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["event_id"] == "TEST-REST-TELEM-PIPE"
    assert data["verified_flag"] is True
    assert data["metadata"]["status"] == "OPERATIONAL"


# ============================================================================
# 6. Model Context Protocol (MCP) Tool Integration
# ============================================================================

def test_mcp_verify_telemetry_seal_tool(mcp_client):
    """Verifies MCP Hub /mcp/invoke executes verify_telemetry_seal tool."""
    station = "STN-MCP-TEST"
    ts = time.time()
    nonce = f"mcp-nonce-{time.perf_counter()}"
    payload = {"precip": 45.0}

    seal = telemetry_security_controller.generate_seal(station, payload, timestamp=ts, nonce=nonce)

    rpc_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "verify_telemetry_seal",
            "arguments": {
                "station_id": station,
                "payload": payload,
                "signature": seal["hmac_sha256_signature"],
                "timestamp_epoch": ts,
                "nonce": nonce
            }
        },
        "id": "mcp-telem-1"
    }
    resp = mcp_client.post("/mcp/invoke", json=rpc_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "mcp-telem-1"
    assert "result" in data
    assert data["result"]["isError"] is False
    assert data["result"]["data"]["is_valid"] is True
    assert data["result"]["data"]["integrity_status"] == "VERIFIED_TAMPER_FREE"
