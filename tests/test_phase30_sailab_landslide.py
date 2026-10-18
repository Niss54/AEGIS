"""
Unit & Integration Tests for Phase 30.1: SailabAlert Multi-Hazard Landslide Coupling & Trilingual Advisory
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.sailab_landslide import (
    sailab_engine,
    HazardTier,
    LandslidePredictRequest
)
from mcp_hub.hub import execute_tool_logic, TOOLS_REGISTRY

client = TestClient(app)


def test_cflsi_mathematical_bounds():
    """Governing invariant: CFLSI must be strictly bounded in [0.0, 1.0]."""
    # Minimum boundary
    cflsi_min = sailab_engine.calculate_cflsi(
        rainfall_mm=0.0,
        river_level_m=0.0,
        soil_moisture_pct=0.0,
        slope_deg=0.0
    )
    assert cflsi_min == 0.0

    # Nominal boundary
    cflsi_max = sailab_engine.calculate_cflsi(
        rainfall_mm=150.0,
        river_level_m=7.0,
        soil_moisture_pct=100.0,
        slope_deg=90.0
    )
    assert 0.99 <= cflsi_max <= 1.0

    # Extreme overflow inputs should clamp gracefully to 1.0
    cflsi_overflow = sailab_engine.calculate_cflsi(
        rainfall_mm=350.0,
        river_level_m=15.0,
        soil_moisture_pct=100.0,
        slope_deg=90.0
    )
    assert cflsi_overflow == 1.0


def test_catastrophic_override_trigger():
    """
    Catastrophic override invariant:
    IF slope > 35° AND soil > 85% AND rain > 100mm -> CATASTROPHIC override active with score >= 0.92.
    """
    req = LandslidePredictRequest(
        rainfall_mm=120.0,
        river_level_m=3.0,
        soil_moisture_pct=90.0,
        slope_deg=42.0,
        location_name="Khandala Ghat, Western Ghats"
    )
    pred = sailab_engine.predict_hazard(req)
    assert pred.is_catastrophic_override is True
    assert pred.hazard_tier == HazardTier.CATASTROPHIC
    assert pred.cflsi_score >= 0.92
    assert pred.confidence >= 0.95


def test_hazard_tier_classification():
    """Verify tier transitions from LOW to CATASTROPHIC."""
    # Low
    low_req = LandslidePredictRequest(
        rainfall_mm=15.0,
        river_level_m=1.0,
        soil_moisture_pct=30.0,
        slope_deg=5.0
    )
    low_res = sailab_engine.predict_hazard(low_req)
    assert low_res.hazard_tier == HazardTier.LOW
    assert low_res.cflsi_score < 0.40

    # Moderate
    mod_req = LandslidePredictRequest(
        rainfall_mm=60.0,
        river_level_m=3.0,
        soil_moisture_pct=60.0,
        slope_deg=18.0
    )
    mod_res = sailab_engine.predict_hazard(mod_req)
    assert mod_res.hazard_tier in [HazardTier.MODERATE, HazardTier.HIGH]


def test_trilingual_advisory_generation():
    """
    Verifies that advisories are generated in authentic English,
    Urdu (اردو script characters present), and Hindi (देवनागरी script characters present).
    """
    req = LandslidePredictRequest(
        rainfall_mm=135.0,
        river_level_m=5.8,
        soil_moisture_pct=88.0,
        slope_deg=40.0,
        location_name="Joshimath Chamoli Corridor"
    )
    pred = sailab_engine.predict_hazard(req)

    # English check
    assert "Joshimath" in pred.advisory_english
    assert any(term in pred.advisory_english.lower() for term in ["alert", "warning", "evacuate", "landslide"])

    # Urdu check (Arabic/Urdu unicode range 0600-06FF)
    assert any("\u0600" <= c <= "\u06ff" for c in pred.advisory_urdu)
    assert "سیلاب" in pred.advisory_urdu or "خطرہ" in pred.advisory_urdu

    # Hindi check (Devanagari unicode range 0900-097F)
    assert any("\u0900" <= c <= "\u097f" for c in pred.advisory_hindi)
    assert "बाढ़" in pred.advisory_hindi or "भूस्खलन" in pred.advisory_hindi


def test_monitoring_stations_catalog():
    """Ensures cross-border monitoring stations are correctly retrieved."""
    stations = sailab_engine.get_stations()
    assert len(stations) >= 6

    # Test India filtering
    india_stns = [s for s in stations if s.country == "India"]
    assert len(india_stns) >= 4
    stn_ids = [s.station_id for s in india_stns]
    assert "STN-WGHAT-01" in stn_ids
    assert "STN-NILGIRI-02" in stn_ids

    # Test Pakistan filtering
    pak_stns = [s for s in stations if s.country == "Pakistan"]
    assert len(pak_stns) >= 2
    pak_ids = [s.station_id for s in pak_stns]
    assert "STN-PAK-05" in pak_ids  # Swat Valley


def test_landslide_api_endpoints():
    """Tests FastAPI REST endpoints under /api/v1/hazard."""
    # 1. Prediction endpoint
    payload = {
        "rainfall_mm": 115.0,
        "river_level_m": 4.5,
        "soil_moisture_pct": 82.0,
        "slope_deg": 32.0,
        "location_name": "Coonoor Nilgiris Basin"
    }
    resp = client.post("/api/v1/hazard/landslide-predict", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "cflsi_score" in data
    assert data["hazard_tier"] in ["MODERATE", "HIGH", "CATASTROPHIC"]
    assert "advisory_urdu" in data
    assert "advisory_hindi" in data

    # 2. Stations endpoint
    stn_resp = client.get("/api/v1/hazard/stations?country=India")
    assert stn_resp.status_code == 200
    stn_list = stn_resp.json()
    assert len(stn_list) >= 4

    # 3. Single station
    single_resp = client.get("/api/v1/hazard/stations/STN-WGHAT-01")
    assert single_resp.status_code == 200
    assert single_resp.json()["station_name"] == "Khandala Ghat Rail & Highway Corridor"

    # 4. Specification endpoint
    spec_resp = client.get("/api/v1/hazard/spec")
    assert spec_resp.status_code == 200
    assert "CFLSI" in spec_resp.json()["governing_invariant"]


def test_mcp_predict_compound_landslide_flood_hazard():
    """Tests integration of predict_compound_landslide_flood_hazard into MCP Hub."""
    assert "predict_compound_landslide_flood_hazard" in TOOLS_REGISTRY

    params = {
        "rainfall_mm": 125.0,
        "river_level_m": 4.8,
        "soil_moisture_pct": 86.0,
        "slope_deg": 36.0,
        "location_name": "Lonavala Khandala Ridge"
    }
    mcp_result = execute_tool_logic("predict_compound_landslide_flood_hazard", params)
    assert "cflsi_score" in mcp_result
    assert mcp_result["cflsi_score"] > 0.60
    assert "advisory_english" in mcp_result
    assert "advisory_urdu" in mcp_result
    assert "advisory_hindi" in mcp_result
