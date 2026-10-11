"""
Tests for Evidence REST API Endpoints (/api/v1/evidence)
Conforms to PRD 2: Section 9, Section 11 and E-097 -> E-108.
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


@pytest.fixture
def sample_evidence_payload():
    return {
        "analysis_id": "test_an_api_001",
        "location_label": "Bandra Kurla Complex, Mumbai",
        "latitude": 19.0660,
        "longitude": 72.8680,
        "weather_vector": {
            "precipitation_24h_mm": 110.5,
            "precipitation_7d_mm": 320.0,
            "soil_saturation_pct": 78.5,
            "relative_humidity_pct": 88.0,
            "elevation_m": 8.5
        },
        "agent1_result": {
            "risk_score": 0.82,
            "risk_tier": "CRITICAL",
            "dominant_factor": "precipitation_24h_mm",
            "model_id": "aegis-flood-classifier-v1",
            "artifact_sha256": "ecf12983bec200fe3d88996c0d89d709676c01deeaa99276dd7f919b23150d70"
        },
        "agent2_result": {
            "exposure_tier": "SEVERE_INUNDATION",
            "waterlogging_depth_cm": 75,
            "buildings_at_risk": 210,
            "drainage_overflow_pct": 85.0,
            "damage_estimate_inr": 85000000.0,
            "methodology": "topographical_heuristic_hazus"
        },
        "agent3_result": {
            "var_estimate_inr": 120000000.0,
            "stranded_asset_risk": "HIGH",
            "compliance_gap_pct": 65,
            "applicable_regulations": ["SEBI BRSR Principle 6", "TCFD Physical Risk"],
            "legal_disclaimer": "This analysis is for research and risk-awareness purposes only."
        },
        "data_mode": "fixture"
    }


def test_create_evidence_bundle_success(sample_evidence_payload):
    """PRD 2: E-097 Evidence creation endpoint creates bundle and computes Keccak-256 digest."""
    response = client.post("/api/v1/evidence", json=sample_evidence_payload)
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["status"] == "CREATED"
    assert data["evidence_id"].startswith("ev_")
    assert data["analysis_id"] == sample_evidence_payload["analysis_id"]
    assert data["schema_version"] == "1.0.0"
    assert data["hash_algorithm"] == "keccak256"
    assert data["canonicalization_version"] == "aegis-canonical-json-v1"
    assert data["digest"].startswith("0x")
    assert len(data["digest"]) == 66  # 0x + 64 hex characters
    assert data["anchor_status"] == "NOT_ANCHORED"

    # Verify bundle structure inside response
    bundle = data["bundle"]
    assert bundle["schema_version"] == "1.0.0"
    assert bundle["evidence_id"] == data["evidence_id"]
    assert bundle["analysis"]["location"]["region_label"] == "Bandra Kurla Complex, Mumbai"
    assert bundle["analysis"]["risk_output"]["risk_tier"] == "CRITICAL"


def test_get_evidence_bundle_by_id(sample_evidence_payload):
    """PRD 2: E-098 Evidence status and retrieval endpoint."""
    create_res = client.post("/api/v1/evidence", json=sample_evidence_payload)
    evidence_id = create_res.json()["evidence_id"]
    expected_digest = create_res.json()["digest"]

    # Now retrieve it
    get_res = client.get(f"/api/v1/evidence/{evidence_id}")
    assert get_res.status_code == 200
    retrieved = get_res.json()

    assert retrieved["evidence_id"] == evidence_id
    assert retrieved["digest"] == expected_digest
    assert retrieved["anchor_status"] == "NOT_ANCHORED"
    assert retrieved["bundle"]["analysis"]["analysis_id"] == sample_evidence_payload["analysis_id"]


def test_get_nonexistent_evidence_returns_404():
    """PRD 2: E-098 Non-existent evidence ID returns 404."""
    response = client.get("/api/v1/evidence/ev_non_existent_999")
    assert response.status_code == 404


def test_verify_evidence_endpoint_pass_and_tamper_detection(sample_evidence_payload):
    """
    PRD 2: E-099 Independent verification endpoint.
    Verifies that pristine bundle passes, and tampered bundle fails with tamper_detected=True.
    """
    # 1. Create a bundle
    create_res = client.post("/api/v1/evidence", json=sample_evidence_payload)
    created_data = create_res.json()
    bundle = created_data["bundle"]
    digest = created_data["digest"]

    # 2. Verify pristine bundle -> PASS
    verify_res = client.post("/api/v1/evidence/verify", json={
        "expected_digest": digest,
        "bundle": bundle
    })
    assert verify_res.status_code == 200
    res_data = verify_res.json()
    assert res_data["status"] == "PASS"
    assert res_data["tamper_detected"] is False
    assert res_data["content_digest_matches"] is True
    assert res_data["computed_digest"] == digest

    # 3. Mutate 1 field in bundle -> FAIL with tamper_detected
    import copy
    tampered_bundle = copy.deepcopy(bundle)
    tampered_bundle["analysis"]["risk_output"]["risk_score"] = 0.15  # tampered down!

    tamper_res = client.post("/api/v1/evidence/verify", json={
        "expected_digest": digest,
        "bundle": tampered_bundle
    })
    assert tamper_res.status_code == 200
    tamper_data = tamper_res.json()
    assert tamper_data["status"] == "FAIL"
    assert tamper_data["tamper_detected"] is True
    assert tamper_data["content_digest_matches"] is False
    assert tamper_data["computed_digest"] != digest

    # 4. Restore original -> PASS again
    restore_res = client.post("/api/v1/evidence/verify", json={
        "expected_digest": digest,
        "bundle": bundle
    })
    assert restore_res.status_code == 200
    assert restore_res.json()["status"] == "PASS"
    assert restore_res.json()["tamper_detected"] is False


def test_create_evidence_invalid_coordinates(sample_evidence_payload):
    """PRD 2: E-008, E-061 Coordinate validation rejects out of bounds."""
    invalid_payload = sample_evidence_payload.copy()
    invalid_payload["latitude"] = 999.0  # Invalid!

    res = client.post("/api/v1/evidence", json=invalid_payload)
    assert res.status_code == 422
