"""
Unit & Integration Test Suite for Phase 29.2:
Ushahidi Multi-Channel Citizen Crisis Crowdsourcing & Verification Engine
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.ushahidi_crisis import (
    ushahidi_engine,
    CitizenIncidentCreate,
    IncidentCategory,
    IncidentSeverity,
    IncidentStatus,
    IngestionChannel
)

client = TestClient(app)


def test_ushahidi_seeded_incidents_presence():
    """Validates that initial pre-seeded real-world Bharat hotspot incidents exist and have sound schemas."""
    incidents = ushahidi_engine.list_incidents()
    assert len(incidents) >= 4

    ids = [inc.incident_id for inc in incidents]
    assert "INC-MUM-001" in ids
    assert "INC-MUM-002" in ids
    assert "INC-BLR-003" in ids
    assert "INC-ASM-004" in ids

    # Kurla trapped civilians incident must be verified with high credibility
    kurla = ushahidi_engine.get_incident("INC-MUM-001")
    assert kurla is not None
    assert kurla.category == IncidentCategory.TRAPPED_CIVILIANS
    assert kurla.credibility_score >= 0.85
    assert kurla.verification_trace is not None
    assert kurla.verification_trace.sar_radar_corroborated is True
    assert kurla.verification_trace.lora_depth_corroborated is True


def test_ushahidi_create_citizen_incident():
    """Tests the submission of a new crowdsourced incident report with initial credibility evaluation."""
    payload = CitizenIncidentCreate(
        title="Dharavi 90-Foot Road Stormwater Overflow",
        description="Drainage culvert blocked with debris. 65cm water surging into transit street.",
        category=IncidentCategory.FLOOD_WATERLOGGING,
        latitude=19.0435,
        longitude=72.8562,
        location_name="Dharavi 90-Foot Road, Mumbai",
        reported_water_depth_cm=65.0,
        civilians_affected=12,
        submitter_name="Sunil Patil",
        submitter_contact="+91-9876543210",
        channel=IngestionChannel.SMS_SYNC
    )

    incident = ushahidi_engine.create_incident(payload)
    assert incident.incident_id.startswith("INC-")
    assert incident.status == IncidentStatus.UNVERIFIED
    assert incident.severity == IncidentSeverity.HIGH
    assert incident.credibility_score > 0.0
    assert incident.witness_count == 1


def test_ushahidi_multi_sensor_verification_formula():
    """
    Validates the multi-sensor reality corroboration formula:
    C_post = 0.20*S_trust + 0.25*min(1.0, N_witness/3) + 0.30*I(SAR <= -3.5dB) + 0.25*min(1.0, D_LoRa / 50cm)
    Verifies that C_post >= 0.75 transitions status to VERIFIED/ESCALATED.
    """
    # Create an unverified incident
    payload = CitizenIncidentCreate(
        title="Sion Circle Subway Submersion",
        description="Stationary municipal bus surrounded by 105cm floodwater.",
        category=IncidentCategory.TRAPPED_CIVILIANS,
        latitude=19.0385,
        longitude=72.8622,
        location_name="Sion Circle Subway, Mumbai",
        reported_water_depth_cm=105.0,
        civilians_affected=25,
        submitter_name="Traffic Police Constable",
        channel=IngestionChannel.WEB_PORTAL
    )
    inc = ushahidi_engine.create_incident(payload)
    assert inc.status == IncidentStatus.UNVERIFIED

    # Execute verification with confirming SAR backscatter (-4.5 dB <= -3.5 dB) and deep LoRa reading (100cm >= 50cm)
    verified_inc = ushahidi_engine.verify_incident(
        incident_id=inc.incident_id,
        simulated_sar_backscatter_db=-4.5,
        simulated_lora_depth_cm=100.0
    )

    assert verified_inc.status in [IncidentStatus.VERIFIED, IncidentStatus.ESCALATED]
    assert verified_inc.credibility_score >= 0.75
    assert verified_inc.verification_trace is not None
    assert verified_inc.verification_trace.sar_radar_corroborated is True
    assert verified_inc.verification_trace.lora_depth_corroborated is True


def test_ushahidi_low_corroboration_scenario():
    """Validates that false or uncorroborated reports (no SAR reflection, dry LoRa gauge) remain UNVERIFIED."""
    payload = CitizenIncidentCreate(
        title="False Alarm Report",
        description="Claiming 200cm water where sensor is dry.",
        category=IncidentCategory.FLOOD_WATERLOGGING,
        latitude=19.1000,
        longitude=72.8500,
        location_name="Bandra West Elevated Ridge",
        reported_water_depth_cm=200.0,
        civilians_affected=2,
        submitter_name="Anonymous Citizen"
    )
    inc = ushahidi_engine.create_incident(payload)

    # Corroborate with SAR backscatter = -1.0 dB (dry/rough surface) and LoRa = 5.0cm (dry)
    verified_inc = ushahidi_engine.verify_incident(
        incident_id=inc.incident_id,
        simulated_sar_backscatter_db=-1.0,
        simulated_lora_depth_cm=5.0
    )

    # Must fail to reach threshold
    assert verified_inc.credibility_score < 0.45
    assert verified_inc.status == IncidentStatus.UNVERIFIED
    assert verified_inc.verification_trace.sar_radar_corroborated is False


def test_ushahidi_add_witness_boosts_credibility():
    """Verifies that adding corroborating witness endorsements increases credibility score."""
    inc = ushahidi_engine.get_incident("INC-BLR-003")
    assert inc is not None
    initial_score = inc.credibility_score

    # Add witness
    updated_inc = ushahidi_engine.add_witness("INC-BLR-003")
    assert updated_inc.witness_count == inc.witness_count
    assert updated_inc.credibility_score >= initial_score


def test_ushahidi_rest_api_endpoints():
    """Tests all FastAPI REST endpoints for Phase 29.2."""
    # 1. POST /api/v1/crisis/incidents
    create_payload = {
        "title": "Chennai Velachery Main Road Waterlogging",
        "description": "Rain runoff 80cm deep, entering residential ground floor apartments.",
        "category": "FLOOD_WATERLOGGING",
        "latitude": 12.9815,
        "longitude": 80.2180,
        "location_name": "Velachery Main Road, Chennai",
        "reported_water_depth_cm": 80.0,
        "civilians_affected": 20,
        "submitter_name": "Velachery Resident",
        "channel": "WEB_PORTAL"
    }
    r_post = client.post("/api/v1/crisis/incidents", json=create_payload)
    assert r_post.status_code == 200
    data_inc = r_post.json()
    new_id = data_inc["incident_id"]
    assert new_id.startswith("INC-")

    # 2. GET /api/v1/crisis/incidents
    r_list = client.get("/api/v1/crisis/incidents?limit=10")
    assert r_list.status_code == 200
    inc_list = r_list.json()
    assert isinstance(inc_list, list)
    assert len(inc_list) >= 5

    # 3. GET /api/v1/crisis/incidents/{incident_id}
    r_get = client.get(f"/api/v1/crisis/incidents/{new_id}")
    assert r_get.status_code == 200
    assert r_get.json()["incident_id"] == new_id

    # 4. POST /api/v1/crisis/verify/{incident_id}
    r_verify = client.post(f"/api/v1/crisis/verify/{new_id}?sar_backscatter_db=-4.2&lora_depth_cm=82.0")
    assert r_verify.status_code == 200
    v_data = r_verify.json()
    assert v_data["credibility_score"] >= 0.75
    assert v_data["status"] in ["VERIFIED", "ESCALATED"]

    # 5. POST /api/v1/crisis/witness/{incident_id}
    r_wit = client.post(f"/api/v1/crisis/witness/{new_id}")
    assert r_wit.status_code == 200
    assert r_wit.json()["witness_count"] >= 2

    # 6. GET /api/v1/crisis/spec
    r_spec = client.get("/api/v1/crisis/spec")
    assert r_spec.status_code == 200
    assert "credibility_formulation" in r_spec.json()
    assert "supported_channels" in r_spec.json()


def test_ushahidi_not_found_handling():
    """Tests 404 response on non-existent incident queries."""
    r = client.get("/api/v1/crisis/incidents/INC-NON-EXISTENT-999")
    assert r.status_code == 404
