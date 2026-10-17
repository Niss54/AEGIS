"""
Phase 28: Automated Test Suite for Autonomous Disaster Evacuation Routing
and Multi-Sensor Parametric Catastrophe Oracle Engine
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.evacuation_routing import evacuation_engine, VehicleType
from backend.app.parametric_oracle import parametric_oracle_engine, OracleConditionInput

client = TestClient(app)


def test_evacuation_routing_ambulance_avoids_submerged_underpass():
    """Verify ambulance pathfinding avoids flooded underpass exceeding clearance limit (40cm)."""
    payload = {
        "origin_name": "Kurla West Lowland Cluster",
        "origin_lat": 19.0685,
        "origin_lon": 72.8792,
        "vehicle_type": "Emergency Ambulance",
        "civilians_count": 30,
        "max_acceptable_risk": "MEDIUM"
    }
    response = client.post("/api/v1/evacuation/routes", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["vehicle_type"] == "Emergency Ambulance"
    assert "MMRDA Ground" in data["destination_shelter"] or "Safe" in data["destination_shelter"]
    assert data["total_distance_km"] > 0.0
    assert data["estimated_time_min"] > 0.0
    assert len(data["waypoints"]) >= 2
    assert data["impassable_segments_avoided"] >= 1
    # Underpass has 135cm water depth, ambulance clearance is 40cm, so underpass must be bypassed
    assert data["max_depth_encountered_cm"] <= 40.0


def test_evacuation_routing_get_query():
    """Verify evacuation route computation via GET query endpoint."""
    response = client.get("/api/v1/evacuation/routes?vehicle_type=Municipal+Rescue+Bus&civilians_count=45")
    assert response.status_code == 200
    data = response.json()
    assert data["total_distance_km"] > 0.0
    assert len(data["turn_by_turn"]) > 0


def test_rescue_fleet_dispatch_and_listing():
    """Verify fleet mobilization endpoint updates status and assigns target sector."""
    resp_dispatch = client.post("/api/v1/evacuation/fleet-dispatch?target_sector=Kurla+West+Lowlands")
    assert resp_dispatch.status_code == 200
    data = resp_dispatch.json()
    assert data["units_mobilized_count"] >= 3
    assert data["target_sector"] == "Kurla West Lowlands"
    assert data["estimated_arrival_min"] <= 15.0

    resp_fleet = client.get("/api/v1/evacuation/fleet")
    assert resp_fleet.status_code == 200
    fleet_data = resp_fleet.json()
    assert len(fleet_data) >= 3

    # Verify boat and bus types
    types = [u["unit_type"] for u in fleet_data]
    assert "NDRF Inflatable Rescue Boat" in types
    assert "Municipal Rescue Bus" in types


def test_parametric_oracle_trigger_satisfied():
    """Verify tripartite oracle invariant triggers payout when all multi-sensor thresholds met."""
    payload = {
        "event_id": "EVT-MITHI-CLOUD-01",
        "location_name": "Mumbai Mithi River Basin",
        "lora_depth_cm": 142.0,      # Threshold >= 100cm (Met)
        "clay_flood_prob": 0.88,     # Threshold >= 0.70 (Met)
        "veda_inundated_sqkm": 14.5, # Threshold >= 5.0 km² (Met)
        "total_beneficiaries": 200,
        "payout_per_beneficiary_inr": 25000.0
    }
    response = client.post("/api/v1/oracle/evaluate-trigger", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["lora_condition_met"] is True
    assert data["clay_condition_met"] is True
    assert data["veda_condition_met"] is True
    assert data["all_conditions_satisfied"] is True
    assert data["payout_eligible"] is True
    assert data["total_liquidity_inr"] == 5000000.0  # 200 * 25,000 = 50 Lakhs INR


def test_parametric_oracle_trigger_unmet_when_depth_low():
    """Verify oracle rejects trigger when physical sensor water depth is below catastrophic threshold."""
    payload = {
        "event_id": "EVT-MITHI-NORMAL-02",
        "location_name": "Mumbai Mithi River Basin",
        "lora_depth_cm": 35.0,       # Below 100cm threshold (Unmet)
        "clay_flood_prob": 0.85,
        "veda_inundated_sqkm": 8.0,
        "total_beneficiaries": 50,
        "payout_per_beneficiary_inr": 25000.0
    }
    response = client.post("/api/v1/oracle/evaluate-trigger", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["lora_condition_met"] is False
    assert data["all_conditions_satisfied"] is False
    assert data["payout_eligible"] is False


def test_parametric_oracle_auto_payout_execution():
    """Verify autonomous smart contract payout execution and on-chain hash generation."""
    payload = {
        "event_id": "EVT-CATASTROPHE-EXEC-01",
        "location_name": "Kurla West Submerged Basin",
        "lora_depth_cm": 155.0,
        "clay_flood_prob": 0.92,
        "veda_inundated_sqkm": 16.0,
        "total_beneficiaries": 100,
        "payout_per_beneficiary_inr": 25000.0
    }
    response = client.post("/api/v1/oracle/auto-payout", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "EXECUTED_ON_POLYGON_AMOY"
    assert data["polygon_tx_hash"].startswith("0x")
    assert data["ipfs_cid"].startswith("bafybeig")
    assert data["total_beneficiaries_paid"] == 100
    assert data["total_payout_amount_inr"] == 2500000.0
    assert len(data["sample_beneficiaries"]) > 0
    assert data["sample_beneficiaries"][0]["wallet_address"].startswith("0x")


def test_evacuation_and_oracle_health_probes():
    """Verify health endpoints."""
    resp_evac = client.get("/api/v1/evacuation/health")
    assert resp_evac.status_code == 200
    assert resp_evac.json()["status"] == "operational"

    resp_oracle = client.get("/api/v1/oracle/health")
    assert resp_oracle.status_code == 200
    assert resp_oracle.json()["status"] == "operational"
