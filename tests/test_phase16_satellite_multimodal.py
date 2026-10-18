"""
TERRA-SENTINEL Phase 16 Automated Test Suite
Module: tests/test_phase16_satellite_multimodal.py
Governance: Gravitas Reliability Runtime · Machine-Checked Verification

Governing Mathematical Equations:
NDWI = (Green - NIR) / (Green + NIR)
NDVI = (NIR - Red) / (NIR + Red)
MNDWI = (Green - SWIR) / (Green + SWIR)
"""

import pytest
import time
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.satellite import (
    compute_spectral_indices,
    EarthObservationController,
    SatelliteObservationModel,
    earth_observation_controller
)
from mcp_hub.hub import execute_tool_logic


@pytest.fixture
def fresh_controller():
    return EarthObservationController()


def test_spectral_indices_mathematical_invariant():
    """
    Verifies mathematical invariants:
    NDWI = (Green - NIR) / (Green + NIR)
    NDVI = (NIR - Red) / (NIR + Red)
    """
    # Test case 1: Typical urban flood inundation (High green, very low NIR, moderate red)
    g, r, n, s = 0.28, 0.18, 0.08, 0.06
    res = compute_spectral_indices(green=g, red=r, nir=n, swir=s)

    expected_ndwi = round((g - n) / (g + n), 4)  # (0.28 - 0.08) / 0.36 = 0.5556
    expected_ndvi = round((n - r) / (n + r), 4)  # (0.08 - 0.18) / 0.26 = -0.3846
    expected_mndwi = round((g - s) / (g + s), 4) # (0.28 - 0.06) / 0.34 = 0.6471

    assert res["ndwi"] == expected_ndwi
    assert res["ndvi"] == expected_ndvi
    assert res["mndwi"] == expected_mndwi
    assert res["water_detection_flag"] is True
    assert res["vegetation_health_flag"] is False
    assert 0.0 <= res["estimated_surface_water_pct"] <= 100.0

    # Test case 2: Heavy vegetation / Non-flooded canopy (High NIR, low red, low green)
    res_veg = compute_spectral_indices(green=0.10, red=0.08, nir=0.65)
    assert res_veg["ndvi"] > 0.5
    assert res_veg["ndwi"] < 0.0
    assert res_veg["water_detection_flag"] is False
    assert res_veg["vegetation_health_flag"] is True

    # Test case 3: Extreme zero boundaries and safety against ZeroDivisionError
    res_zero = compute_spectral_indices(green=0.0, red=0.0, nir=0.0)
    assert res_zero["ndwi"] == 0.0
    assert res_zero["ndvi"] == 0.0

    # Test case 4: Physical bounds [-1.0, 1.0]
    res_clamped = compute_spectral_indices(green=1.5, red=-0.5, nir=0.0)
    assert -1.0 <= res_clamped["ndwi"] <= 1.0
    assert -1.0 <= res_clamped["ndvi"] <= 1.0


@pytest.mark.asyncio
async def test_earth_observation_controller_pipeline(fresh_controller):
    """
    Verifies PRD Phase 16 execution invariant:
    result.verified_flag is True, result.metadata['status'] == 'OPERATIONAL'
    """
    payload = {
        "event_id": "TEST-PHASE-16",
        "telemetry": 42.0,
        "lat": 19.0728,
        "lon": 72.8797,
        "green": 0.28,
        "red": 0.18,
        "nir": 0.08
    }
    result = await fresh_controller.execute_phase_pipeline(payload)
    assert isinstance(result, SatelliteObservationModel)
    assert result.event_id == "TEST-PHASE-16"
    assert result.verified_flag is True
    assert result.metadata["status"] == "OPERATIONAL"
    assert "data" in result.metadata
    assert result.metadata["data"]["spectral_indices"]["water_detection_flag"] is True


@pytest.mark.asyncio
async def test_circuit_breaker_transitions(fresh_controller):
    """
    Verifies 3-tier circuit breaker:
    3 failures -> OPEN -> Tier 2 local fallback -> 30s cooldown -> HALF_OPEN probe -> CLOSED.
    """
    assert fresh_controller.circuit_state == "CLOSED"

    # Trigger 3 failures
    for i in range(3):
        await fresh_controller.execute_phase_pipeline({
            "event_id": f"FAIL-{i}",
            "force_fallback": True
        })

    assert fresh_controller.circuit_state == "OPEN"
    health = fresh_controller.get_health()
    assert health["circuit_state"] == "OPEN"
    assert health["status"] == "DEGRADED_FALLBACK"

    # Execution during OPEN routes to TIER_2_LOCAL_FALLBACK
    fallback_res = await fresh_controller.execute_phase_pipeline({
        "event_id": "TEST-FALLBACK"
    })
    assert fallback_res.execution_tier == "TIER_2_LOCAL_FALLBACK"

    # Simulate 31s cooldown elapsed
    fresh_controller.last_failure_time = time.time() - 31.0
    assert fresh_controller._check_circuit() == "HALF_OPEN"

    # Successful probe restores to CLOSED
    success_res = await fresh_controller.execute_phase_pipeline({
        "event_id": "TEST-PROBE",
        "force_fallback": False
    })
    assert success_res.execution_tier == "ENTERPRISE_PROD"
    assert fresh_controller.circuit_state == "CLOSED"


def test_satellite_rest_endpoints():
    """
    Verifies FastAPI REST endpoints in backend/app/routes/satellite.py
    """
    client = TestClient(app)

    # 1. Compute spectral indices
    resp_indices = client.post("/satellite/indices/compute", json={
        "green": 0.28,
        "red": 0.18,
        "nir": 0.08,
        "swir": 0.06
    })
    assert resp_indices.status_code == 200
    data = resp_indices.json()
    assert data["ndwi"] > 0
    assert "NDWI = (Green - NIR) / (Green + NIR)" in data["governing_equations"]["NDWI"]

    # 2. Subsystem health
    resp_health = client.get("/satellite/phase16/health")
    assert resp_health.status_code == 200
    assert resp_health.json()["phase"] == 16

    # 3. Operational pipeline
    resp_pipe = client.post("/satellite/phase16/pipeline", json={
        "event_id": "TEST-REST-P16",
        "lat": 19.0728,
        "lon": 72.8797
    })
    assert resp_pipe.status_code == 200
    assert resp_pipe.json()["event_id"] == "TEST-REST-P16"
    assert resp_pipe.json()["verified_flag"] is True

    # 4. Standard ingestion endpoint
    resp_ingest = client.post("/satellite/ingest", json={
        "lat": 19.0728,
        "lon": 72.8797,
        "location_name": "Mumbai Mithi River Basin"
    })
    assert resp_ingest.status_code == 200
    assert "copernicus_sentinel2" in resp_ingest.json()

    # 5. Layer GeoJSON
    resp_layers = client.get("/satellite/layers/mumbai?lat=19.0728&lon=72.8797&depth_cm=80")
    assert resp_layers.status_code == 200
    assert resp_layers.json()["type"] == "FeatureCollection"


def test_mcp_hub_phase16_tools():
    """
    Verifies MCP Hub dispatching for Phase 16 tools.
    """
    # 1. compute_satellite_spectral_indices
    res_indices = execute_tool_logic("compute_satellite_spectral_indices", {
        "green": 0.28,
        "red": 0.18,
        "nir": 0.08
    })
    assert "ndwi" in res_indices
    assert res_indices["water_detection_flag"] is True

    # 2. ingest_earth_observation_telemetry
    res_ingest = execute_tool_logic("ingest_earth_observation_telemetry", {
        "lat": 19.0728,
        "lon": 72.8797
    })
    assert res_ingest["status"] == "success"
    assert "copernicus_sentinel2" in res_ingest

    # 3. analyze_satellite_imagery
    res_analyze = execute_tool_logic("analyze_satellite_imagery", {
        "lat": 19.0728,
        "lon": 72.8797,
        "location_name": "Mumbai Mithi River Basin",
        "depth_cm": 85
    })
    assert "gemini_multimodal_analysis" in res_analyze
