"""
AEGIS-CLIMATE: Phase 26 Verification Suite
Tests the Google Research State-Handoff LSTM Hydrology Engine & DeepMind DGMR Nowcasting Engine.
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.hydrology_sequence import (
    hydrology_sequence_engine,
    deepmind_nowcast_engine,
    CatchmentDescriptors
)

client = TestClient(app)


def test_catchment_embedding_calculation():
    """Verify SCS-CN and topographical slope embed into consistent runoff factor."""
    c_urban = CatchmentDescriptors(
        basin_area_km2=20.0,
        slope_gradient=0.04,
        curve_number_cn=90.0  # High urban imperviousness
    )
    c_rural = CatchmentDescriptors(
        basin_area_km2=20.0,
        slope_gradient=0.01,
        curve_number_cn=60.0  # High soil infiltration
    )

    alpha_urban = hydrology_sequence_engine._compute_catchment_embedding(c_urban)
    alpha_rural = hydrology_sequence_engine._compute_catchment_embedding(c_rural)

    # Urban impervious basin must have higher runoff acceleration factor than rural basin
    assert alpha_urban > alpha_rural
    assert 0.15 <= alpha_rural <= 1.50
    assert 0.30 <= alpha_urban <= 2.50


def test_state_handoff_72h_progression():
    """Verify 0-72h lead-time progression generates monotonic and valid hydrograph curves."""
    res = hydrology_sequence_engine.predict_lead_time_progression(
        lat=19.0760,
        lon=72.8777,
        location_name="Mumbai Mithi Basin",
        precipitation_24h_mm=120.0,
        soil_saturation_pct=85.0,
        elevation_m=8.0,
        drainage_capacity_index=45.0
    )

    assert res.status == "success"
    assert len(res.progression_72h) == 9  # [0, 3, 6, 12, 18, 24, 36, 48, 72]
    assert res.peak_discharge_m3_s > 0
    assert res.peak_stage_m > 0
    assert 0 <= res.peak_lead_time_hours <= 72

    # Verify P10 <= P50 <= P90 confidence quantile ordering across all steps
    for step in res.progression_72h:
        assert step.confidence_p10 <= step.confidence_p50 <= step.confidence_p90
        assert 0.0 <= step.confidence_p10 <= 1.0
        assert 0.0 <= step.confidence_p90 <= 1.0
        assert step.hazard_state in ["NORMAL", "ADVISORY", "WARNING", "CRITICAL"]


def test_deepmind_dgmr_nowcasting_exceedance():
    """Verify DeepMind DGMR 0-120 minute precipitation nowcasting & exceedance probabilities."""
    steps = deepmind_nowcast_engine.predict_nowcast_exceedance(
        current_rain_rate_mm_hr=75.0,
        soil_saturation_pct=85.0,
        trend="intensifying"
    )

    assert len(steps) == 9  # [0, 15, 30, 45, 60, 75, 90, 105, 120]
    
    for s in steps:
        assert 0 <= s.minute <= 120
        assert s.predicted_rain_rate_mm_hr >= 0.0
        # Exceedance probabilities must be between 0 and 1
        assert 0.0 <= s.p_exceed_20mm_hr <= 1.0
        assert 0.0 <= s.p_exceed_50mm_hr <= 1.0
        assert 0.0 <= s.p_exceed_80mm_hr <= 1.0
        # Monotonicity of exceedance thresholds: P(R > 20) >= P(R > 50) >= P(R > 80)
        assert s.p_exceed_20mm_hr >= s.p_exceed_50mm_hr >= s.p_exceed_80mm_hr
        assert s.convective_severity_tier in ["GREEN", "YELLOW", "ORANGE", "RED"]

    # High intensity rain (75mm/hr) must trigger RED or ORANGE tier at peak
    severities = [s.convective_severity_tier for s in steps]
    assert "RED" in severities or "ORANGE" in severities


def test_rest_api_forecast_progression_post():
    """Verify POST /api/v1/forecast/progression endpoint."""
    payload = {
        "lat": 19.0760,
        "lon": 72.8777,
        "location_name": "Bengaluru Outer Ring Road",
        "precipitation_24h_mm": 110.0,
        "soil_saturation_pct": 82.0,
        "elevation_m": 920.0,
        "drainage_capacity_index": 40.0,
        "basin_area_km2": 18.0,
        "slope_gradient": 0.03,
        "curve_number_cn": 85.0
    }
    res = client.post("/api/v1/forecast/progression", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "success"
    assert data["location_name"] == "Bengaluru Outer Ring Road"
    assert len(data["progression_72h"]) > 0
    assert len(data["nowcast_120m"]) > 0
    assert "Google Research State-Handoff" in data["model_architecture"]


def test_rest_api_forecast_progression_get():
    """Verify GET /api/v1/forecast/progression endpoint query parameters."""
    res = client.get("/api/v1/forecast/progression?lat=19.0760&lon=72.8777&precipitation_24h_mm=60.0")
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "success"
    assert "progression_72h" in data
    assert "nowcast_120m" in data
    assert data["peak_discharge_m3_s"] > 0
