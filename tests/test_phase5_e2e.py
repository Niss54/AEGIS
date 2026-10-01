"""
Phase 5 End-to-End Integration & Cockpit Verification Suite for AEGIS-CLIMATE
Validates full API stack, What-If scenario simulation, multi-tier GeoJSON payloads,
and compiled Vite production bundle artifacts.
"""
import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_phase5_hotspots_contract():
    """Verify frontend hotspot contract has all required fields."""
    res = client.get("/api/v1/hotspots")
    assert res.status_code == 200
    hotspots = res.json()
    assert len(hotspots) >= 5

    required_keys = {"id", "name", "state", "lat", "lon", "risk_profile", "description", "typical_annual_loss_inr"}
    for h in hotspots:
        assert required_keys.issubset(h.keys())
        assert isinstance(h["lat"], (int, float))
        assert isinstance(h["lon"], (int, float))
        assert h["risk_profile"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def test_phase5_what_if_simulation_cascade():
    """Verify What-If simulation slider inputs trigger the autonomous 3-agent cascade."""
    # Cloudburst simulation: +110mm rainfall, 92% soil saturation
    res = client.post("/api/v1/analyze", json={
        "lat": 19.0728,
        "lon": 72.8797,
        "location_name": "Mumbai — Mithi River & Kurla Basin",
        "radius_km": 10.0,
        "simulated_additional_rain_mm": 110.0,
        "simulated_saturation_pct_override": 92.0
    })
    assert res.status_code == 200
    data = res.json()

    # Agent 1 Validation
    assert "agent1" in data
    assert data["agent1"]["risk_tier"] in ["HIGH", "CRITICAL"]
    assert data["agent1"]["risk_score"] > 0.65
    assert data["agent1"]["triggered_chronic"] is True

    # Agent 2 Validation
    assert "agent2" in data
    assert data["agent2"] is not None
    assert data["agent2"]["waterlogging_depth_cm"] >= 50
    assert data["agent2"]["buildings_at_risk"] > 0
    assert "horizon_curves" in data["agent2"]
    assert "10yr" in data["agent2"]["horizon_curves"]

    # Agent 3 Validation
    assert "agent3" in data
    assert data["agent3"] is not None
    assert data["agent3"]["var_estimate_inr"] > 0
    assert len(data["agent3"]["applicable_regulations"]) >= 1
    assert data["agent3"]["bilingual_alert_hindi"] is not None
    assert data["agent3"]["bilingual_alert_english"] is not None

    # Agent Thought Trace Monologue
    assert len(data["thought_trace"]) >= 5
    agent_ids = {step["agent_id"] for step in data["thought_trace"]}
    assert "agent-1-acute" in agent_ids
    assert "agent-2-chronic" in agent_ids
    assert "agent-3-financial" in agent_ids


def test_phase5_geojson_spatial_layers():
    """Verify GeoJSON multi-tier layers returned for the Leaflet GIS map."""
    res = client.get("/api/v1/geo/layer/evt-mumbai-sim?lat=19.0728&lon=72.8797&depth_cm=88&severity=INFRASTRUCTURE_FAILURE")
    assert res.status_code == 200
    geojson = res.json()

    assert geojson["type"] == "FeatureCollection"
    features = geojson["features"]
    assert len(features) >= 4

    layer_types = {f["properties"].get("layer") for f in features if "layer" in f.get("properties", {})}
    assert "inundation_moderate" in layer_types
    assert "inundation_core" in layer_types
    assert "drainage_conduit" in layer_types

    # Verify at least one critical asset point
    asset_points = [f for f in features if f["geometry"]["type"] == "Point"]
    assert len(asset_points) >= 1
    assert "projected_depth_cm" in asset_points[0]["properties"]


def test_phase5_frontend_production_build():
    """Verify frontend compiled artifacts exist and are ready for serving."""
    frontend_dir = Path("frontend")
    dist_dir = frontend_dir / "dist"
    index_html = dist_dir / "index.html"
    assets_dir = dist_dir / "assets"

    assert dist_dir.exists(), "frontend/dist does not exist! Run npm run build."
    assert index_html.exists(), "frontend/dist/index.html is missing!"
    assert index_html.stat().st_size > 500, "frontend/dist/index.html is unexpectedly small."

    js_files = list(assets_dir.glob("*.js"))
    css_files = list(assets_dir.glob("*.css"))
    assert len(js_files) >= 1, "Compiled JS bundle missing in frontend/dist/assets"
    assert len(css_files) >= 1, "Compiled CSS bundle missing in frontend/dist/assets"

    # Verify brand logo
    logo_file = frontend_dir / "public" / "logo.png"
    assert logo_file.exists(), "frontend/public/logo.png is missing!"


if __name__ == "__main__":
    test_phase5_hotspots_contract()
    print("[PASS] test_phase5_hotspots_contract")
    test_phase5_what_if_simulation_cascade()
    print("[PASS] test_phase5_what_if_simulation_cascade")
    test_phase5_geojson_spatial_layers()
    print("[PASS] test_phase5_geojson_spatial_layers")
    test_phase5_frontend_production_build()
    print("[PASS] test_phase5_frontend_production_build")
    print("[PASS] All Phase 5 End-to-End Tests Passed Successfully!")
