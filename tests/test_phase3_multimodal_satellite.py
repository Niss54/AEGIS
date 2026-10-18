"""
Phase 3 Verification Test Suite: Multimodal Earth Observation Integration
Tests Copernicus Sentinel-2 MSI (NDWI/NDVI), ISRO Bhuvan NRSC Geology,
Google Earth Engine 30m SRTM DEM, and Gemini 2.0 Flash Multimodal Spatial Reasoning.
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.satellite import earth_observation_engine

client = TestClient(app)


def test_copernicus_sentinel2_spectral_indices():
    """Verify Sentinel-2 MSI L2A metadata and mathematical NDWI/NDVI formulas."""
    meta = earth_observation_engine.get_sentinel2_metadata(lat=19.0728, lon=72.8797)
    assert meta["constellation"] == "Copernicus Sentinel-2B MSI L2A"
    assert "mgrs_tile_id" in meta
    assert meta["ground_sampling_distance_m"] == 10.0

    indices = meta["spectral_indices"]
    assert -1.0 <= indices["ndwi"] <= 1.0
    assert -1.0 <= indices["ndvi"] <= 1.0
    assert -1.0 <= indices["mndwi"] <= 1.0
    assert 0.0 <= indices["estimated_surface_water_pct"] <= 100.0


def test_isro_bhuvan_geology_mapping():
    """Verify ISRO Bhuvan Indian National Remote Sensing Centre basin classification."""
    bhuvan = earth_observation_engine.get_isro_bhuvan_geology(lat=19.0728, lon=72.8797)
    assert "ISRO Bhuvan" in bhuvan["provider"]
    assert "Mithi" in bhuvan["river_basin"]
    assert "Zone 4" in bhuvan["nrsc_flood_hazard_zone"]


def test_google_earth_engine_dem_slope():
    """Verify GEE NASA SRTM 30m elevation kernel and slope calculation."""
    dem = earth_observation_engine.get_google_earth_engine_dem(lat=19.0728, lon=72.8797, elevation_m=12.0)
    assert "Google Earth Engine" in dem["source"]
    assert dem["raster_resolution"] == "1 Arc-Second (30-meter ground pixel)"
    assert dem["slope_gradient_pct"] >= 0.0
    assert len(dem["elevation_3x3_kernel"]) == 3


def test_multispectral_geojson_layer_generation():
    """Verify dynamic GeoJSON generation with NDWI contours."""
    geojson = earth_observation_engine.generate_multispectral_geojson(lat=19.0728, lon=72.8797, depth_cm=85)
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) >= 2
    polygon_feature = geojson["features"][0]
    assert polygon_feature["geometry"]["type"] == "Polygon"
    assert polygon_feature["properties"]["layer"] == "Copernicus_Sentinel2_NDWI_FloodExtent"
    assert polygon_feature["properties"]["inundation_depth_cm"] == 85


def test_gemini_multimodal_spatial_reasoning():
    """Verify Gemini 2.0 Flash multimodal spatial reasoning synthesis."""
    res = earth_observation_engine.analyze_satellite_multimodal(
        lat=19.0728,
        lon=72.8797,
        location_name="Mumbai Mithi River Basin",
        depth_cm=85,
        weather_summary="Monsoon cloudburst 120mm"
    )
    assert res["status"] == "success"
    assert "satellite_provenance" in res
    assert "bhuvan_geology" in res
    assert "google_earth_engine_dem" in res
    assert len(res["gemini_multimodal_analysis"]) > 40
    assert "SPATIAL VERDICT" in res["gemini_multimodal_analysis"] or "Sentinel" in res["gemini_multimodal_analysis"]


def test_rest_api_satellite_ingest():
    """Verify POST /api/v1/satellite/ingest REST endpoint."""
    res = client.post("/api/v1/satellite/ingest", json={
        "lat": 19.0728,
        "lon": 72.8797,
        "location_name": "Mumbai Mithi River Basin",
        "elevation_m": 12.0
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "copernicus_sentinel2" in data
    assert "isro_bhuvan" in data
    assert "google_earth_engine_dem" in data


def test_rest_api_satellite_multimodal_analysis():
    """Verify POST /api/v1/satellite/analyze-multimodal REST endpoint."""
    res = client.post("/api/v1/satellite/analyze-multimodal", json={
        "lat": 19.0728,
        "lon": 72.8797,
        "location_name": "Mumbai Mithi River Basin",
        "waterlogging_depth_cm": 85,
        "weather_summary": "Active storm"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "gemini_multimodal_analysis" in data


def test_rest_api_satellite_layers():
    """Verify GET /api/v1/satellite/layers/{id} endpoint returns GeoJSON."""
    res = client.get("/api/v1/satellite/layers/mumbai-mithi?lat=19.0728&lon=72.8797&depth_cm=85")
    assert res.status_code == 200
    geojson = res.json()
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) > 0


def test_mcp_satellite_tool_invocation():
    """Verify analyze_satellite_imagery tool execution via MCP JSON-RPC 2.0 Gateway."""
    res = client.post("/mcp/invoke", json={
        "jsonrpc": "2.0",
        "method": "analyze_satellite_imagery",
        "params": {
            "lat": 19.0728,
            "lon": 72.8797,
            "location_name": "Mumbai Mithi River Basin",
            "depth_cm": 85
        },
        "id": "sat-req-1"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["jsonrpc"] == "2.0"
    assert "result" in data
    result = data["result"]
    assert result["status"] == "success"
    assert "satellite_provenance" in result
    assert "spectral_indices" in result
    assert "gemini_multimodal_analysis" in result

