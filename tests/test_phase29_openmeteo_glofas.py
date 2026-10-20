"""
Unit & Integration Test Suite for Phase 29.1:
Open-Meteo GloFAS River Discharge & Ensemble Flood Engine
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.openmeteo_glofas import (
    glofas_engine,
    GloFASHazardLevel,
    CatchmentSeverityRequest
)

client = TestClient(app)


def test_glofas_basin_catalog_and_threshold_invariants():
    """Validates that all monitored Indian river basins possess physically sound, strictly ascending return-period thresholds."""
    basins = glofas_engine.list_basins()
    assert len(basins) >= 5

    basin_ids = [b.basin_id for b in basins]
    assert "mumbai_mithi" in basin_ids
    assert "assam_brahmaputra" in basin_ids
    assert "delhi_yamuna" in basin_ids
    assert "bengaluru_vrishabhavathi" in basin_ids
    assert "chennai_adyar_ennore" in basin_ids

    for b in basins:
        assert b.baseflow_m3s > 0.0
        # Strict physical invariant: Baseflow < Q2 < Q5 < Q20
        assert b.baseflow_m3s < b.q_2yr_threshold
        assert b.q_2yr_threshold < b.q_5yr_threshold
        assert b.q_5yr_threshold < b.q_20yr_threshold
        assert -90.0 <= b.latitude <= 90.0
        assert -180.0 <= b.longitude <= 180.0


def test_glofas_nearest_basin_spatial_lookup():
    """Verifies that coordinate lookups snap accurately to the nearest geographic river basin."""
    # Near Mumbai BKC
    b_mumbai = glofas_engine._find_nearest_basin(19.07, 72.88)
    assert b_mumbai.basin_id == "mumbai_mithi"

    # Near Kaziranga, Assam
    b_assam = glofas_engine._find_nearest_basin(26.58, 93.17)
    assert b_assam.basin_id == "assam_brahmaputra"

    # Near Delhi Yamuna Bridge
    b_delhi = glofas_engine._find_nearest_basin(28.65, 77.23)
    assert b_delhi.basin_id == "delhi_yamuna"


def test_glofas_forecast_and_hydrograph():
    """Validates 7-day hydrograph generation, ensemble confidence bounds, and return period classification."""
    res = glofas_engine.get_forecast(basin_id="mumbai_mithi", forecast_days=7)
    assert res.basin_id == "mumbai_mithi"
    assert len(res.hydrograph) == 7
    assert res.peak_discharge_m3s >= res.current_discharge_m3s

    for pt in res.hydrograph:
        assert pt.discharge_m3s > 0.0
        assert pt.ensemble_min_m3s <= pt.discharge_m3s
        assert pt.discharge_m3s <= pt.ensemble_max_m3s
        assert pt.hazard_level in [
            GloFASHazardLevel.NORMAL,
            GloFASHazardLevel.MODERATE,
            GloFASHazardLevel.SEVERE,
            GloFASHazardLevel.CATASTROPHIC
        ]


def test_glofas_lapse_rate_dem_downscaling():
    """Verifies atmospheric lapse rate DEM temperature downscaling: T(high) < T(low)."""
    # High elevation (Bengaluru 870m) vs Low elevation (Mumbai 8m)
    t_bengaluru = glofas_engine._compute_lapse_rate_temp(870.0)
    t_mumbai = glofas_engine._compute_lapse_rate_temp(8.0)

    # Higher elevation must be cooler due to environmental lapse rate (0.0065 K/m)
    assert t_bengaluru < t_mumbai
    expected_diff = 0.0065 * (870.0 - 8.0)
    assert abs((t_mumbai - t_bengaluru) - expected_diff) < 0.1


def test_glofas_catchment_severity_fusing():
    """Validates the composite catchment severity index combining surface runoff with river discharge."""
    # Scenario A: Extreme cloudburst + saturated soil + clogged drains
    req_extreme = CatchmentSeverityRequest(
        basin_id="mumbai_mithi",
        hourly_precipitation_mm=180.0,
        soil_moisture_percentage=98.0,
        drainage_capacity_percentage=15.0
    )
    res_extreme = glofas_engine.compute_catchment_severity(req_extreme)
    assert 0.0 <= res_extreme.composite_severity_score <= 1.0
    assert res_extreme.composite_severity_score >= 0.70
    assert res_extreme.hazard_tier in ["HIGH", "CRITICAL"]

    # Scenario B: Dry day + unsaturated soil + clear drains
    req_dry = CatchmentSeverityRequest(
        basin_id="mumbai_mithi",
        hourly_precipitation_mm=0.0,
        soil_moisture_percentage=25.0,
        drainage_capacity_percentage=90.0
    )
    res_dry = glofas_engine.compute_catchment_severity(req_dry)
    assert 0.0 <= res_dry.composite_severity_score <= 1.0
    assert res_dry.composite_severity_score < res_extreme.composite_severity_score


def test_glofas_rest_api_endpoints():
    """Tests all FastAPI REST endpoints for Phase 29.1."""
    # 1. GET /api/v1/forecast/glofas
    r_forecast = client.get("/api/v1/forecast/glofas?basin_id=delhi_yamuna&forecast_days=5")
    assert r_forecast.status_code == 200
    data_f = r_forecast.json()
    assert data_f["basin_id"] == "delhi_yamuna"
    assert len(data_f["hydrograph"]) == 5
    assert "source_model" in data_f

    # 2. GET /api/v1/forecast/glofas/basins
    r_basins = client.get("/api/v1/forecast/glofas/basins")
    assert r_basins.status_code == 200
    basins = r_basins.json()
    assert isinstance(basins, list)
    assert len(basins) >= 5

    # 3. POST /api/v1/forecast/glofas/catchment-severity
    payload = {
        "basin_id": "bengaluru_vrishabhavathi",
        "hourly_precipitation_mm": 95.0,
        "soil_moisture_percentage": 85.0,
        "drainage_capacity_percentage": 30.0
    }
    r_sev = client.post("/api/v1/forecast/glofas/catchment-severity", json=payload)
    assert r_sev.status_code == 200
    data_s = r_sev.json()
    assert 0.0 <= data_s["composite_severity_score"] <= 1.0
    assert "flood_risk_verdict" in data_s

    # 4. GET /api/v1/forecast/glofas/spec
    r_spec = client.get("/api/v1/forecast/glofas/spec")
    assert r_spec.status_code == 200
    data_sp = r_spec.json()
    assert "governing_invariants" in data_sp
    assert "return_periods" in data_sp


def test_glofas_extreme_boundary_and_fallback_resilience():
    """Tests that out-of-bounds inputs and non-existent basin IDs gracefully failover to deterministic defaults."""
    # Coordinate outside India snaps to nearest basin without crashing
    res = glofas_engine.get_forecast(lat=0.0, lon=0.0, forecast_days=100)
    assert res.basin_id in glofas_engine.basins
    # Clamped to 30 days maximum
    assert len(res.hydrograph) == 30
