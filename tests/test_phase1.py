"""
Phase 1 Integration & Sanity Tests for AEGIS-CLIMATE
Tests Health Check, Bharat Hotspots, Geo Layers, and Full Multi-Agent Cascade.
"""
import sys
import os
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify backend and services status."""
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "operational"
    assert "fastapi_backend" in data["services"]
    assert data["services"]["fastapi_backend"] == "online"


def test_hotspots_endpoint():
    """Verify preloaded Bharat climate hotspots."""
    res = client.get("/api/v1/hotspots")
    assert res.status_code == 200
    hotspots = res.json()
    assert len(hotspots) >= 5
    ids = [h["id"] for h in hotspots]
    assert "mumbai-mithi" in ids
    assert "bengaluru-bellandur" in ids
    assert "assam-kaziranga" in ids


def test_geo_layer_endpoint():
    """Verify GeoJSON polygon generation for Leaflet."""
    res = client.get("/api/v1/geo/layer/evt-test-1?lat=19.0728&lon=72.8797&depth_cm=85")
    assert res.status_code == 200
    geojson = res.json()
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) > 0
    # First feature should be inundation polygon
    poly = geojson["features"][0]
    assert poly["geometry"]["type"] == "Polygon"


def test_analyze_low_risk_scenario():
    """Test nominal condition where Agent 1 returns LOW/MEDIUM and halts cascade."""
    res = client.post("/api/v1/analyze", json={
        "lat": 26.9124,
        "lon": 75.7873,  # Jaipur (dry)
        "location_name": "Jaipur Semi-Arid Zone",
        "simulated_additional_rain_mm": 0.0,
        "simulated_saturation_pct_override": 25.0
    })
    assert res.status_code == 200
    data = res.json()
    assert data["agent1"]["risk_score"] < 0.65
    assert data["agent1"]["triggered_chronic"] is False
    assert data["agent2"] is None
    assert data["agent3"] is None
    assert len(data["thought_trace"]) >= 3


def test_analyze_cascading_high_risk_scenario():
    """Test monsoon cloudburst trigger where Agent 1 triggers Agent 2, which triggers Agent 3."""
    res = client.post("/api/v1/analyze", json={
        "lat": 19.0728,
        "lon": 72.8797,  # Mumbai Mithi River
        "location_name": "Mumbai Mithi River Basin",
        "simulated_additional_rain_mm": 90.0,
        "simulated_saturation_pct_override": 92.0
    })
    assert res.status_code == 200
    data = res.json()
    assert data["agent1"]["risk_score"] >= 0.65
    assert data["agent1"]["triggered_chronic"] is True
    # Agent 2 must be populated
    assert data["agent2"] is not None
    assert data["agent2"]["waterlogging_depth_cm"] > 0
    assert data["agent2"]["buildings_at_risk"] > 0
    # Agent 3 must be populated
    assert data["agent3"] is not None
    assert data["agent3"]["var_estimate_inr"] > 0
    assert data["agent3"]["bilingual_alert_hindi"] is not None
    # Thought trace must show the full reasoning monologue
    assert len(data["thought_trace"]) >= 5


if __name__ == "__main__":
    print("Running AEGIS Phase 1 Integration Tests...")
    test_health_endpoint()
    print("[PASS] test_health_endpoint passed")
    test_hotspots_endpoint()
    print("[PASS] test_hotspots_endpoint passed")
    test_geo_layer_endpoint()
    print("[PASS] test_geo_layer_endpoint passed")
    test_analyze_low_risk_scenario()
    print("[PASS] test_analyze_low_risk_scenario passed")
    test_analyze_cascading_high_risk_scenario()
    print("[PASS] test_analyze_cascading_high_risk_scenario passed")
    print(">>> ALL PHASE 1 INTEGRATION TESTS PASSED PERFECTLY! <<<")
