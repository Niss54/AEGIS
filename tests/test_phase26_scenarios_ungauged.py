"""
TERRA-SENTINEL: Phase 4 Verification Suite
Extreme Disaster Scenarios Presets & Google Research Ungauged Basin Hydrology
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_ungauged_basin_forecast_endpoint():
    """Verifies Google Research zero-shot ungauged catchment transfer & synthetic rating curve."""
    response = client.get(
        "/api/v1/forecast/ungauged-basin",
        params={
            "lat": 19.0760,
            "lon": 72.8777,
            "location_name": "Mithi Uninstrumented Ward L",
            "basin_area_km2": 15.0,
            "slope_gradient": 0.02,
            "curve_number_cn": 85.0
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["location_name"] == "Mithi Uninstrumented Ward L"
    assert data["regional_cluster_id"] == "Cluster-IND-WestCoast-Urban"
    assert data["donor_gauged_basin"] == "Vaitarna Coastal Hydrometric Post V-12"
    assert data["transfer_confidence_pct"] >= 85.0
    assert data["runoff_coefficient"] > 0.50
    assert data["concentration_time_hours"] > 0.0

    rating_curve = data["synthetic_rating_curve"]
    assert len(rating_curve) == 9
    # Monotonicity check
    for i in range(len(rating_curve) - 1):
        assert rating_curve[i]["stage_m"] < rating_curve[i + 1]["stage_m"]
        assert rating_curve[i]["discharge_m3_s"] < rating_curve[i + 1]["discharge_m3_s"]


def test_scenario_presets_endpoint():
    """Verifies curated extreme disaster scenario presets catalog."""
    response = client.get("/api/v1/scenarios/presets")
    assert response.status_code == 200
    presets = response.json()
    assert len(presets) == 3
    preset_ids = [p["id"] for p in presets]
    assert "mithi_cloudburst" in preset_ids
    assert "kurla_sluice_jam" in preset_ids
    assert "dharavi_storm_surge" in preset_ids


def test_scenario_simulate_endpoint_preset():
    """Verifies end-to-end atomic simulation of Mithi Cloudburst scenario."""
    response = client.post(
        "/api/v1/scenarios/simulate",
        json={"scenario_id": "mithi_cloudburst"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["scenario"]["id"] == "mithi_cloudburst"

    # Multi-agent unified risk
    risk = data["unified_risk"]
    assert risk["agent1"]["risk_score"] > 0.70
    assert risk["agent1"]["metrics"]["precipitation_24h_mm"] > 50.0

    # Hydrology progression
    hydro = data["hydrology_progression"]
    assert len(hydro["progression_72h"]) == 9
    assert len(hydro["nowcast_120m"]) == 9
    assert hydro["peak_discharge_m3_s"] > 0.0

    # SOP guidance
    sop = data["disaster_management_sop"]
    assert sop["ndma_level"] == "LEVEL-3 SEVERE ALERT"
    assert "Open downstream tidal lock gates" in sop["sluice_gate_instruction"]
    assert sop["civic_evacuation_radius_km"] > 0.0


def test_scenario_simulate_invalid_request():
    """Verifies 400 Bad Request when neither scenario_id nor custom_parameters are passed."""
    response = client.post("/api/v1/scenarios/simulate", json={})
    assert response.status_code == 400
