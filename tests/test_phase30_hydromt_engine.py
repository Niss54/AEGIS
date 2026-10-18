"""
Unit & Integration Tests for Phase 30.2: Deltares HydroMT Computational Hydrography & TWI Engine
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.hydromt_engine import (
    hydromt_engine,
    DelineateRequest,
    LandCoverType,
    MANNING_ROUGHNESS
)
from mcp_hub.hub import execute_tool_logic, TOOLS_REGISTRY

client = TestClient(app)


def test_basin_catalog_and_retrieval():
    """Verify basin catalog indexing and single-basin retrieval."""
    basins = hydromt_engine.list_basins()
    assert len(basins) >= 5
    basin_ids = [b.basin_id for b in basins]
    assert "mumbai_mithi" in basin_ids
    assert "delhi_yamuna" in basin_ids
    assert "assam_brahmaputra" in basin_ids

    mithi = hydromt_engine.get_basin("mumbai_mithi")
    assert mithi is not None
    assert mithi.state == "Maharashtra"
    assert mithi.outlet_elevation_m < mithi.ridge_elevation_m
    assert mithi.total_area_sqkm > 0.0

    non_existent = hydromt_engine.get_basin("unknown_basin_xyz")
    assert non_existent is None


def test_dem_slope_gradient_and_d8_routing():
    """Verify D8 flow direction assignment and physical non-negative slope invariant."""
    req = DelineateRequest(
        basin_id="mumbai_mithi",
        grid_size=8,
        cell_resolution_m=30.0,
        inflow_precipitation_mm=80.0,
        land_cover=LandCoverType.URBAN_IMPERVIOUS
    )
    res = hydromt_engine.delineate_catchment(req)

    assert len(res.twi_matrix) == 8
    assert len(res.twi_matrix[0]) == 8
    assert res.total_catchment_area_sqkm > 0.0
    assert res.peak_overland_velocity_ms > 0.0
    assert res.time_of_concentration_min > 0.0


def test_twi_mathematical_bounds_and_formula():
    """
    Governing invariant: TWI = ln(alpha / (tan(beta) + 1e-4)).
    Mean TWI must be positive and bounded within realistic geomorphological range [0, 30].
    """
    req = DelineateRequest(
        basin_id="bengaluru_vrishabhavathi",
        grid_size=10,
        cell_resolution_m=25.0,
        inflow_precipitation_mm=100.0,
        land_cover=LandCoverType.URBAN_IMPERVIOUS
    )
    res = hydromt_engine.delineate_catchment(req)

    assert res.mean_twi > 0.0
    assert res.max_twi >= res.mean_twi
    assert res.max_twi <= 35.0
    assert "ln(alpha / (tan(beta) + 1e-4))" in res.governing_invariant


def test_manning_overland_velocity_and_roughness():
    """
    Governing invariant: Manning overland velocity v = (1/n) * R_h^(2/3) * S_0^(1/2).
    A smoother surface (URBAN_IMPERVIOUS, n=0.015) must yield a higher peak velocity
    than a rough surface (MANGROVE_WETLAND, n=0.080) on identical topography.
    """
    req_urban = DelineateRequest(
        basin_id="mumbai_mithi",
        grid_size=8,
        cell_resolution_m=30.0,
        inflow_precipitation_mm=120.0,
        land_cover=LandCoverType.URBAN_IMPERVIOUS
    )
    res_urban = hydromt_engine.delineate_catchment(req_urban)

    req_mangrove = DelineateRequest(
        basin_id="mumbai_mithi",
        grid_size=8,
        cell_resolution_m=30.0,
        inflow_precipitation_mm=120.0,
        land_cover=LandCoverType.MANGROVE_WETLAND
    )
    res_mangrove = hydromt_engine.delineate_catchment(req_mangrove)

    assert res_urban.manning_roughness_n < res_mangrove.manning_roughness_n
    assert res_urban.peak_overland_velocity_ms > res_mangrove.peak_overland_velocity_ms
    assert res_urban.time_of_concentration_min < res_mangrove.time_of_concentration_min


def test_critical_depression_sinks_identification():
    """Verify that critical depressions (TWI >= 12.0) are accurately identified."""
    req = DelineateRequest(
        basin_id="chennai_adyar",
        grid_size=12,
        cell_resolution_m=20.0,
        inflow_precipitation_mm=150.0,
        land_cover=LandCoverType.URBAN_IMPERVIOUS
    )
    res = hydromt_engine.delineate_catchment(req)

    assert res.critical_depression_cells_count == len(res.depression_sinks)
    for sink in res.depression_sinks:
        assert sink.twi_score >= 12.0
        assert sink.is_depression_sink is True


def test_hydromt_rest_api_endpoints():
    """Verify FastAPI endpoints mounted at /api/v1/hydromt/*."""
    # List basins
    r_list = client.get("/api/v1/hydromt/basins")
    assert r_list.status_code == 200
    assert len(r_list.json()) >= 5

    # Get single basin
    r_single = client.get("/api/v1/hydromt/basins/delhi_yamuna")
    assert r_single.status_code == 200
    assert r_single.json()["basin_name"] == "Yamuna Delhi Floodplain Reach"

    # Get single basin 404
    r_404 = client.get("/api/v1/hydromt/basins/non_existent_corridor")
    assert r_404.status_code == 404

    # GET TWI calculation
    r_twi = client.get("/api/v1/hydromt/twi?basin_id=mumbai_mithi&grid_size=6")
    assert r_twi.status_code == 200
    data_twi = r_twi.json()
    assert "mean_twi" in data_twi
    assert len(data_twi["twi_matrix"]) == 6

    # POST Delineate
    payload = {
        "basin_id": "assam_brahmaputra",
        "grid_size": 8,
        "cell_resolution_m": 30.0,
        "inflow_precipitation_mm": 110.0,
        "land_cover": "FOREST_CANOPY"
    }
    r_post = client.post("/api/v1/hydromt/delineate", json=payload)
    assert r_post.status_code == 200
    data_post = r_post.json()
    assert data_post["basin_id"] == "assam_brahmaputra"
    assert data_post["manning_roughness_n"] == 0.060

    # Spec
    r_spec = client.get("/api/v1/hydromt/spec")
    assert r_spec.status_code == 200
    assert "topographic_wetness_index" in r_spec.json()["governing_invariants"]


def test_hydromt_mcp_tool_execution():
    """Verify MCP Tool delineation invocation in tools registry and hub."""
    assert "delineate_catchment_twi" in TOOLS_REGISTRY

    params = {
        "basin_id": "mumbai_mithi",
        "grid_size": 6,
        "cell_resolution_m": 30.0,
        "inflow_precipitation_mm": 90.0,
        "land_cover": "URBAN_IMPERVIOUS"
    }
    result = execute_tool_logic("delineate_catchment_twi", params)
    assert result["basin_id"] == "mumbai_mithi"
    assert "mean_twi" in result
    assert "twi_matrix" in result
    assert len(result["twi_matrix"]) == 6
