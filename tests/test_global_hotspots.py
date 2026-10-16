"""
Phase 1 Test Suite: Global Climate Hotspot & Multi-National Ingestion Engine
Verifies Türkiye, USA, Estonia, and India UP hotspots, Nested Jurisdictional Tagging,
and Gridded Telemetry Anomaly Ratios.
"""
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.routes.hotspots import GLOBAL_HOTSPOTS
from backend.app.weather.adapter import weather_adapter, WeatherSourceAdapter
from backend.app.weather.schemas import WeatherVector, WeatherAdapterResult
from backend.app.schemas import JurisdictionHierarchy


client = TestClient(app)


def test_all_ten_hotspots_loaded():
    """Verify that all 10 strategic multi-national climate hotspots are configured."""
    assert len(GLOBAL_HOTSPOTS) == 10
    ids = {h.id for h in GLOBAL_HOTSPOTS}
    assert "lucknow-gomti" in ids
    assert "istanbul-marmara" in ids
    assert "kastamonu-bozkurt" in ids
    assert "orange-county-santa-ana" in ids
    assert "parnu-baltic" in ids
    assert "mumbai-mithi" in ids
    assert "bengaluru-bellandur" in ids
    assert "assam-kaziranga" in ids


def test_nested_jurisdiction_hierarchy():
    """Verify that every hotspot contains a complete Yale-OpenClimate nested jurisdiction hierarchy."""
    for hotspot in GLOBAL_HOTSPOTS:
        assert hotspot.jurisdiction is not None, f"Hotspot {hotspot.id} missing jurisdiction"
        assert hotspot.jurisdiction.country_iso in {"IN", "TR", "US", "EE"}
        assert len(hotspot.jurisdiction.country_name) > 0
        assert len(hotspot.jurisdiction.admin1_state) > 0
        assert len(hotspot.jurisdiction.admin2_district) > 0
        assert len(hotspot.jurisdiction.basin_name) > 0
        assert hotspot.historical_baseline_24h_mm > 0.0


def test_hotspots_api_endpoint_returns_all_ten():
    """Verify GET /api/v1/hotspots returns the full multi-national catalog."""
    resp = client.get("/api/v1/hotspots")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 10
    
    # Check Lucknow (UP)
    lucknow = next(h for h in data if h["id"] == "lucknow-gomti")
    assert lucknow["state"] == "Uttar Pradesh"
    assert lucknow["country"] == "India"
    assert lucknow["jurisdiction"]["basin_name"] == "Gomti River Basin"
    assert lucknow["typical_annual_loss_inr"] == "₹380 Crores"

    # Check Istanbul (Türkiye)
    istanbul = next(h for h in data if h["id"] == "istanbul-marmara")
    assert istanbul["country"] == "Türkiye"
    assert istanbul["jurisdiction"]["country_iso"] == "TR"
    assert istanbul["lat"] == pytest.approx(41.0082, 0.001)

    # Check Orange County (USA)
    oc = next(h for h in data if h["id"] == "orange-county-santa-ana")
    assert oc["country"] == "United States"
    assert oc["lon"] == pytest.approx(-117.8311, 0.001)

    # Check Pärnu (Estonia)
    parnu = next(h for h in data if h["id"] == "parnu-baltic")
    assert parnu["country"] == "Estonia"
    assert parnu["jurisdiction"]["country_iso"] == "EE"


def test_weather_adapter_global_coordinates_validation():
    """Verify coordinate validation allows global longitudes (including negative for Americas)."""
    # Negative longitude (Orange County, California)
    WeatherSourceAdapter.validate_coordinates(33.7175, -117.8311)
    
    # Northern latitude (Estonia)
    WeatherSourceAdapter.validate_coordinates(58.3859, 24.4971)

    # Mediterranean latitude (Istanbul, Türkiye)
    WeatherSourceAdapter.validate_coordinates(41.0082, 28.9784)

    # Gangetic plain (Lucknow, UP)
    WeatherSourceAdapter.validate_coordinates(26.8467, 80.9462)

    # Rejection of invalid coordinates
    with pytest.raises(Exception):
        WeatherSourceAdapter.validate_coordinates(95.0, 72.0)
    with pytest.raises(Exception):
        WeatherSourceAdapter.validate_coordinates(19.0, -185.0)


def test_weather_adapter_deterministic_fixtures_for_global_hotspots():
    """Verify deterministic benchmark fixtures return calibrated values for international locations."""
    fixtures = ["istanbul", "bozkurt", "orange_county", "parnu", "lucknow", "cloudburst", "arid", "moderate"]
    for scenario in fixtures:
        res = weather_adapter.get_deterministic_fixture(scenario)
        assert isinstance(res, WeatherAdapterResult)
        assert res.provenance.data_mode == "fixture"
        assert res.provenance.is_synthetic is True
        assert res.vector.precipitation_anomaly_ratio >= 0.0
        assert res.vector.historical_baseline_24h_mm > 0.0

    # Specific assertions
    ist_res = weather_adapter.get_deterministic_fixture("istanbul")
    assert ist_res.vector.precipitation_24h_mm == 95.0
    assert ist_res.provenance.query_coordinates["latitude"] == pytest.approx(41.0082, 0.001)

    oc_res = weather_adapter.get_deterministic_fixture("orange_county")
    assert oc_res.vector.precipitation_24h_mm == 105.0
    assert oc_res.provenance.query_coordinates["longitude"] == pytest.approx(-117.8311, 0.001)

    lucknow_res = weather_adapter.get_deterministic_fixture("lucknow")
    assert lucknow_res.vector.precipitation_24h_mm == 120.0
    assert lucknow_res.provenance.query_coordinates["latitude"] == pytest.approx(26.8467, 0.001)


def test_weather_adapter_synthetic_fallbacks_by_region():
    """Verify regional synthetic fallback correctly detects coordinate bounding boxes."""
    # California coordinate
    cal_fallback = weather_adapter.get_synthetic_fallback(33.72, -117.83, reason="Test CA fallback")
    assert cal_fallback.vector.historical_baseline_24h_mm == 18.0
    assert cal_fallback.vector.precipitation_24h_mm == 105.0
    assert cal_fallback.provenance.is_synthetic is True

    # Istanbul coordinate
    ist_fallback = weather_adapter.get_synthetic_fallback(41.01, 28.98, reason="Test TR fallback")
    assert ist_fallback.vector.historical_baseline_24h_mm == 28.0
    assert ist_fallback.vector.precipitation_24h_mm == 95.0

    # Lucknow coordinate
    luck_fallback = weather_adapter.get_synthetic_fallback(26.85, 80.95, reason="Test UP fallback")
    assert luck_fallback.vector.historical_baseline_24h_mm == 42.0
    assert luck_fallback.vector.precipitation_24h_mm == 120.0

    # Pärnu coordinate
    parnu_fallback = weather_adapter.get_synthetic_fallback(58.39, 24.50, reason="Test EE fallback")
    assert parnu_fallback.vector.historical_baseline_24h_mm == 22.0
    assert parnu_fallback.vector.precipitation_24h_mm == 75.0


def test_anomaly_ratio_calculation():
    """Verify precipitation anomaly ratio calculation conforms to dClimate specifications."""
    # When precip_24h = 140 and baseline = 35 -> anomaly = 4.0
    fixture = weather_adapter.get_deterministic_fixture("bozkurt")
    expected_ratio = round(140.0 / 35.0, 2)
    assert fixture.vector.precipitation_anomaly_ratio == expected_ratio == 4.0
