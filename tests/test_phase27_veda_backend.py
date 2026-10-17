"""
Phase 27.2: Automated Test Suite for NASA VEDA STAC & Dynamic COG Raster Service
Derived from NASA-IMPACT/veda-backend (TiTiler + STAC FastAPI Architecture)
"""

import io
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from backend.app.main import app
from backend.app.veda_raster import veda_engine, VedaRasterEngine

client = TestClient(app)


def test_stac_collections_listing():
    """Verify STAC collections endpoint returns conforming STAC v1.0.0 collections."""
    response = client.get("/api/v1/stac/collections")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 4

    collection_ids = [c["id"] for c in data]
    assert "sentinel-2-l2a" in collection_ids
    assert "sentinel-1-rtc" in collection_ids
    assert "copernicus-dem-glo-30" in collection_ids
    assert "veda-flood-inundation" in collection_ids

    # Validate STAC v1.0.0 structure
    for c in data:
        assert "extent" in c
        assert "spatial" in c["extent"]
        assert "temporal" in c["extent"]
        assert "links" in c
        assert "license" in c


def test_stac_collection_by_id():
    """Verify retrieving specific STAC collection metadata and 404 handling."""
    resp = client.get("/api/v1/stac/collections/sentinel-1-rtc")
    assert resp.status_code == 200
    item = resp.json()
    assert item["id"] == "sentinel-1-rtc"
    assert "sar" in item["keywords"]

    # Test non-existent collection
    resp404 = client.get("/api/v1/stac/collections/non-existent-collection-id")
    assert resp404.status_code == 404


def test_stac_search_spatial_bbox():
    """Test STAC spatial search using POST request with bounding box."""
    payload = {
        "collections": ["veda-flood-inundation", "sentinel-1-rtc"],
        "bbox": [72.75, 18.90, 73.05, 19.30],
        "limit": 5
    }
    response = client.post("/api/v1/stac/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) >= 2

    for feat in data["features"]:
        assert feat["type"] == "Feature"
        assert "geometry" in feat
        assert feat["geometry"]["type"] == "Polygon"
        assert "assets" in feat
        assert "cog_data" in feat["assets"]
        assert "visual" in feat["assets"]
        assert feat["assets"]["cog_data"]["type"] == "image/tiff; application=geotiff; profile=cloud-optimized"


def test_stac_search_get_query():
    """Test STAC search using GET query parameters."""
    response = client.get("/api/v1/stac/search?bbox=72.80,19.00,72.90,19.10&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) > 0


def test_dynamic_slippy_map_raster_tile_generation():
    """Test dynamic generation of Slippy Map Web Mercator PNG tiles."""
    # Zoom=12, x=2874, y=1770 (Mumbai area)
    response = client.get("/api/v1/raster/tile/12/2874/1770?collection_id=veda-flood-inundation&colormap_name=blues")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.headers["X-NASA-VEDA-Engine"] == "TiTiler-Dynamic-COG"

    # Verify binary PNG signature (\x89PNG\r\n\x1a\n)
    raw_bytes = response.content
    assert raw_bytes.startswith(b"\x89PNG\r\n\x1a\n")

    # Verify valid RGBA image decodable by PIL
    img = Image.open(io.BytesIO(raw_bytes))
    assert img.format == "PNG"
    assert img.size == (256, 256)
    assert img.mode == "RGBA"


def test_sar_radar_and_dem_tiles():
    """Test dynamic tiles with SAR radar colormap and DEM elevation."""
    resp_sar = client.get("/api/v1/raster/tile/12/2874/1770?collection_id=sentinel-1-rtc&colormap_name=sar_radar")
    assert resp_sar.status_code == 200
    img_sar = Image.open(io.BytesIO(resp_sar.content))
    assert img_sar.size == (256, 256)

    resp_dem = client.get("/api/v1/raster/tile/12/2874/1770?collection_id=copernicus-dem-glo-30&colormap_name=viridis")
    assert resp_dem.status_code == 200
    img_dem = Image.open(io.BytesIO(resp_dem.content))
    assert img_dem.size == (256, 256)


def test_sub_50ms_zonal_statistics():
    """Verify sub-50ms zonal statistics engine metrics computation."""
    payload = {
        "collection_id": "veda-flood-inundation",
        "bbox": [72.82, 19.02, 72.90, 19.12],
        "variable": "water_depth_m",
        "pixel_resolution_m": 30.0
    }
    response = client.post("/api/v1/raster/statistics", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["variable"] == "water_depth_m"
    assert data["total_pixels"] > 0
    assert data["inundation_area_sqkm"] >= 0.0
    assert "percentiles" in data
    assert "p50" in data["percentiles"]
    assert "p90" in data["percentiles"]
    assert data["dominant_risk_tier"] in ["LOW", "MODERATE", "SEVERE", "CATASTROPHIC"]

    # Verify sub-50ms execution speed
    assert data["execution_time_ms"] < 50.0, f"Expected sub-50ms, got {data['execution_time_ms']}ms"


def test_circuit_breaker_resilience_and_fallback():
    """Verify 3-tier circuit breaker trips to OPEN and delivers fallback tile."""
    test_engine = VedaRasterEngine()
    test_engine.consecutive_failures = 3
    test_engine.circuit_state = "OPEN"
    test_engine.last_failure_time = 0  # expired cooldown

    # In HALF-OPEN or fallback mode, generate_raster_tile must safely return valid PNG
    tile = test_engine.generate_raster_tile(10, 500, 300)
    assert tile.startswith(b"\x89PNG\r\n\x1a\n")
    img = Image.open(io.BytesIO(tile))
    assert img.size == (256, 256)


def test_raster_pipeline_and_health_endpoints():
    """Verify diagnostic status and health endpoints."""
    resp_pipeline = client.get("/api/v1/raster/pipeline")
    assert resp_pipeline.status_code == 200
    data = resp_pipeline.json()
    assert data["status"] == "operational"
    assert "registered_collections" in data
    assert "colormaps_available" in data

    resp_health = client.get("/api/v1/raster/health")
    assert resp_health.status_code == 200
    assert resp_health.json()["status"] == "operational"
