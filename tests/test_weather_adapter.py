"""
Tests for Meteorological Source Adapter
Conforms to PRD 2: E-024 Source adapter tests.
Validates independent rolling windows, range checks, synthetic fallbacks, and cache.
"""
import pytest
from unittest.mock import AsyncMock, patch
from backend.app.weather.adapter import WeatherSourceAdapter
from backend.app.weather.cache import WeatherCache
from backend.app.weather.schemas import WeatherAdapterResult
from backend.app.errors import ValidationError


def test_coordinate_validation_accepts_valid():
    adapter = WeatherSourceAdapter()
    adapter.validate_coordinates(19.0728, 72.8797)  # Mumbai
    adapter.validate_coordinates(-33.8688, 151.2093)  # Sydney
    adapter.validate_coordinates(0.0, 0.0)


def test_coordinate_validation_rejects_out_of_bounds():
    adapter = WeatherSourceAdapter()
    with pytest.raises(ValidationError):
        adapter.validate_coordinates(95.0, 72.0)  # Lat > 90

    with pytest.raises(ValidationError):
        adapter.validate_coordinates(-91.0, 72.0)  # Lat < -90

    with pytest.raises(ValidationError):
        adapter.validate_coordinates(19.0, 185.0)  # Lon > 180

    with pytest.raises(ValidationError):
        adapter.validate_coordinates(19.0, -181.0)  # Lon < -180


def test_synthetic_fallback_schema_flags():
    """PRD 2: E-023 Verify fallback carries is_synthetic=True and fallback_reason."""
    adapter = WeatherSourceAdapter()
    res = adapter.get_synthetic_fallback(19.0728, 72.8797, reason="Network timeout test")
    assert res.provenance.is_synthetic is True
    assert res.provenance.data_mode == "synthetic"
    assert "Network timeout" in (res.provenance.fallback_reason or "")
    assert res.vector.precipitation_7d_mm > res.vector.precipitation_24h_mm
    assert 0.0 <= res.vector.soil_saturation_pct <= 100.0


def test_deterministic_fixtures():
    adapter = WeatherSourceAdapter()
    cloudburst = adapter.get_deterministic_fixture("cloudburst")
    assert cloudburst.vector.precipitation_24h_mm >= 100.0
    assert cloudburst.vector.soil_saturation_pct >= 90.0
    assert cloudburst.provenance.data_mode == "fixture"

    arid = adapter.get_deterministic_fixture("arid")
    assert arid.vector.precipitation_24h_mm == 0.0
    assert arid.vector.soil_saturation_pct <= 25.0


def test_cache_key_normalization():
    """PRD 2: E-020 Cached weather vectors keyed by normalized coordinates."""
    cache = WeatherCache(default_ttl_seconds=60)
    key1 = cache.build_key(19.0728123, 72.8797456)
    key2 = cache.build_key(19.0728999, 72.8797111)
    # Both round to 19.073 and 72.880
    assert key1 == key2

    adapter = WeatherSourceAdapter()
    fixture = adapter.get_deterministic_fixture("arid")
    cache.set(19.0728, 72.8797, fixture)

    retrieved = cache.get(19.0729, 72.8796)
    assert retrieved is not None
    assert retrieved.cached is True


def test_independent_seven_day_rainfall_logic():
    """PRD 2: E-014 7-day rainfall must be from its own series, not 24h * 2.8."""
    adapter = WeatherSourceAdapter()
    fb = adapter.get_synthetic_fallback(19.0728, 72.8797)
    # 24h is 78.5, 7d is 195.0. 78.5 * 2.8 = 219.8 != 195.0
    assert abs(fb.vector.precipitation_7d_mm - (fb.vector.precipitation_24h_mm * 2.8)) > 1.0


@pytest.mark.asyncio
async def test_live_fetch_offline_resilience():
    """Simulates provider timeout and verifies resilient fallback with provenance."""
    adapter = WeatherSourceAdapter(base_url="https://invalid-non-existent-weather-domain.local")
    result = await adapter.fetch_weather_vector(19.0728, 72.8797, use_cache=False)
    assert result.provenance.is_synthetic is True
    assert result.vector.precipitation_24h_mm > 0.0
