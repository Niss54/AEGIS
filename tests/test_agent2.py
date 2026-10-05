"""
AEGIS-CLIMATE — Agent 2 (Chronic Climate Vulnerability & Geospatial Engine) Test Suite
Validates 30m SRTM DEM elevation modeling, HAZUS depth-damage curves, GeoJSON layers, and MCP tool execution.
"""
import sys
import os
import time

sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.agent2_geo import chronic_geo_engine, interpolate_damage_fraction
from mcp_hub.hub import app as mcp_app

backend_client = TestClient(app)
mcp_client = TestClient(mcp_app)


def test_hazus_damage_curves():
    """Verify HAZUS-MH depth-damage curve interpolation."""
    # Depth 0 cm -> 0% damage
    assert interpolate_damage_fraction("critical_infrastructure", 0) == 0.0
    # Depth 30 cm -> ~40% damage for critical infra
    d30 = interpolate_damage_fraction("critical_infrastructure", 30)
    assert 0.35 <= d30 <= 0.45
    # Depth 90 cm -> > 85% damage
    d90 = interpolate_damage_fraction("critical_infrastructure", 90)
    assert d90 >= 0.85
    # Residential curve at 30cm -> ~20%
    d_res_30 = interpolate_damage_fraction("residential_masonry", 30)
    assert 0.18 <= d_res_30 <= 0.25
    print(f"[PASS] HAZUS depth-damage curves verified: CritInfra@30cm={d30*100:.1f}%, Res@30cm={d_res_30*100:.1f}%")


def test_structural_exposure_engine():
    """Verify Chronic Vulnerability Engine calculation."""
    res = chronic_geo_engine.analyze_structural_exposure(
        lat=19.0728,
        lon=72.8797,
        risk_score=0.88,
        precipitation_24h_mm=110.0,
        soil_saturation_pct=92.0,
        elevation_m=8.0,
        radius_km=10.0
    )
    assert res["status"] == "COMPLETED"
    assert res["exposure_tier"] == "INFRASTRUCTURE_FAILURE"
    assert res["waterlogging_depth_cm"] >= 60
    assert res["drainage_overflow_pct"] >= 70.0
    assert res["buildings_at_risk"] >= 200
    assert res["damage_estimate_inr"] > 50_000_000
    assert res["damage_estimate_usd"] > 600_000
    # Multi-decade horizon curves check
    hc = res["horizon_curves"]
    assert hc["10yr"] <= hc["20yr"] <= hc["30yr"]
    print(f"[PASS] Chronic Engine calculation: Depth={res['waterlogging_depth_cm']}cm, Overflow={res['drainage_overflow_pct']}%, Loss=INR {res['damage_estimate_inr']:,}")


def test_geojson_layers_generation():
    """Verify GIS FeatureCollection structure and layers."""
    geojson = chronic_geo_engine.generate_geojson_layers(
        event_id="evt-geo-test",
        lat=19.0728,
        lon=72.8797,
        depth_cm=85,
        severity="INFRASTRUCTURE_FAILURE"
    )
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) >= 4

    layers = [f["properties"].get("layer") for f in geojson["features"]]
    assert "inundation_core" in layers
    assert "inundation_moderate" in layers
    assert "drainage_conduit" in layers
    assert "critical_asset" in layers
    print(f"[PASS] GeoJSON multi-layer GIS generation: {len(geojson['features'])} features (Core, Secondary, Canals, Assets)")


def test_tools_geo_exposure_endpoint():
    """Test POST /api/v1/tools/geo-exposure REST endpoint."""
    payload = {
        "lat": 19.0728,
        "lon": 72.8797,
        "risk_score": 0.85,
        "precipitation_24h_mm": 95.0,
        "soil_saturation_pct": 88.0,
        "elevation_m": 12.0,
        "radius_km": 10.0
    }
    res = backend_client.post("/api/v1/tools/geo-exposure", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["COMPLETED", "success"]
    assert data["tool"] == "compute_dem_exposure"
    assert data["exposure_tier"] == "INFRASTRUCTURE_FAILURE"
    print(f"[PASS] /api/v1/tools/geo-exposure endpoint working: Tier={data['exposure_tier']}, Depth={data['waterlogging_depth_cm']}cm")


def test_events_structural_endpoint():
    """Test full workflow and GET /api/v1/events/{id}/structural."""
    # First trigger analysis
    analyze_res = backend_client.post("/api/v1/analyze", json={
        "lat": 19.0728,
        "lon": 72.8797,
        "location_name": "Mumbai Mithi River Basin",
        "simulated_additional_rain_mm": 85.0,
        "simulated_saturation_pct_override": 90.0
    })
    assert analyze_res.status_code == 200
    event_data = analyze_res.json()
    event_id = event_data["event_id"]

    # Now fetch structural report for this event
    res = backend_client.get(f"/api/v1/events/{event_id}/structural")
    assert res.status_code == 200
    struct_data = res.json()
    assert struct_data["status"] == "COMPLETED"
    assert struct_data["waterlogging_depth_cm"] > 0
    assert struct_data["buildings_at_risk"] > 0
    assert "10yr" in struct_data["horizon_curves"]
    print(f"[PASS] /api/v1/events/{event_id}/structural endpoint retrieved structural report")


def test_mcp_hub_compute_dem_exposure():
    """Test calling compute_dem_exposure through MCP Hub JSON-RPC 2.0."""
    rpc_payload = {
        "jsonrpc": "2.0",
        "method": "compute_dem_exposure",
        "params": {
            "lat": 19.0728,
            "lon": 72.8797,
            "risk_score": 0.85,
            "precipitation_24h_mm": 100.0,
            "soil_saturation_pct": 90.0,
            "elevation_m": 10.0,
            "radius_km": 10.0
        },
        "id": "mcp-test-agent2"
    }
    res = mcp_client.post("/mcp/invoke", json=rpc_payload)
    assert res.status_code == 200
    resp_data = res.json()
    assert "result" in resp_data
    result = resp_data["result"]
    assert result["exposure_tier"] == "INFRASTRUCTURE_FAILURE"
    assert "damage_estimate_inr" in result
    print(f"[PASS] MCP Hub JSON-RPC dispatch: Tool returned tier={result['exposure_tier']}, Loss=INR {result['damage_estimate_inr']:,}")


if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING AGENT 2 (CHRONIC GEOSPATIAL) TEST SUITE")
    print("=" * 60)
    test_hazus_damage_curves()
    test_structural_exposure_engine()
    test_geojson_layers_generation()
    test_tools_geo_exposure_endpoint()
    test_events_structural_endpoint()
    test_mcp_hub_compute_dem_exposure()
    print("=" * 60)
    print(">>> ALL AGENT 2 CHRONIC GEOSPATIAL TESTS PASSED (100%)! <<<")
    print("=" * 60)
