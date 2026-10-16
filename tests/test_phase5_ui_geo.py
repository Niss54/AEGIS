"""
Test Suite for Phase 5: Automated Geolocation-Aware Radar & Multi-National UI Expansion
Verifies:
1. POST /api/v1/geo/detect-location reverse-geocoding & nearest hotspot snapping:
   - Lucknow, UP (User Home Base) -> lucknow-gomti (Hindi / Devanagari)
   - Istanbul, Türkiye -> istanbul-marmara (Turkish / Türkçe)
   - Pärnu, Estonia -> parnu-baltic (Estonian / Eesti keel)
   - Orange County, USA -> orange-county-santa-ana (Spanish / English)
   - Mumbai, Maharashtra -> mumbai-mithi (Marathi / Devanagari)
2. Haversine distance calculations and jurisdictional tagging.
3. Geo layer rendering endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.routes.geo import haversine_km


@pytest.fixture
def client():
    return TestClient(app)


def test_haversine_km():
    # Distance between Lucknow (26.8467, 80.9462) and Kanpur (26.4499, 80.3319) is approx 75-85 km
    dist = haversine_km(26.8467, 80.9462, 26.4499, 80.3319)
    assert 70.0 <= dist <= 90.0


def test_detect_location_lucknow(client):
    res = client.post(
        "/api/v1/geo/detect-location",
        json={"lat": 26.8467, "lon": 80.9462}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["nearest_hotspot"]["id"] == "lucknow-gomti"
    assert data["distance_km"] < 1.0
    assert data["language_profile"]["code"] == "hi-IN"
    assert data["language_profile"]["short_code"] == "hi"
    assert data["language_profile"]["currency_symbol"] == "₹"


def test_detect_location_istanbul(client):
    res = client.post(
        "/api/v1/geo/detect-location",
        json={"lat": 41.0082, "lon": 28.9784}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["nearest_hotspot"]["id"] == "istanbul-marmara"
    assert data["distance_km"] < 1.0
    assert data["language_profile"]["code"] == "tr-TR"
    assert data["language_profile"]["name"] == "Turkish"
    assert data["language_profile"]["flag_emoji"] == "🇹🇷"
    assert data["language_profile"]["currency_symbol"] == "₺"


def test_detect_location_parnu_estonia(client):
    res = client.post(
        "/api/v1/geo/detect-location",
        json={"lat": 58.3859, "lon": 24.4971}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["nearest_hotspot"]["id"] == "parnu-baltic"
    assert data["distance_km"] < 1.0
    assert data["language_profile"]["code"] == "et-EE"
    assert data["language_profile"]["native_name"] == "Eesti keel"
    assert data["language_profile"]["flag_emoji"] == "🇪🇪"
    assert data["language_profile"]["currency_symbol"] == "€"


def test_detect_location_orange_county(client):
    res = client.post(
        "/api/v1/geo/detect-location",
        json={"lat": 33.7175, "lon": -117.8311}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["nearest_hotspot"]["id"] == "orange-county-santa-ana"
    assert data["distance_km"] < 1.0
    assert data["language_profile"]["code"] == "es-US"
    assert data["language_profile"]["flag_emoji"] == "🇺🇸"


def test_detect_location_mumbai(client):
    res = client.post(
        "/api/v1/geo/detect-location",
        json={"lat": 19.0728, "lon": 72.8797}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["nearest_hotspot"]["id"] == "mumbai-mithi"
    assert data["distance_km"] < 1.0
    assert data["language_profile"]["code"] == "mr-IN"
    assert data["language_profile"]["native_name"] == "मराठी"


def test_geo_layer_endpoint(client):
    res = client.get("/api/v1/geo/layer/evt-test-p5?lat=26.8467&lon=80.9462&depth_cm=70")
    assert res.status_code == 200
    data = res.json()
    assert data.get("type") == "FeatureCollection"
    assert "features" in data
    assert len(data["features"]) > 0
