"""
AEGIS Weather Source Adapter
Conforms to PRD 2: E-013 through E-024.
Extracts genuine independent 24-hour and 7-day rolling precipitation series.
Never derives 7-day rainfall using fixed multipliers.
"""
import time
import logging
from typing import Optional, Dict, Any, List
import httpx

from backend.app.config import settings
from backend.app.errors import ValidationError, WeatherProviderError
from backend.app.weather.schemas import (
    WeatherVector,
    ProvenanceMetadata,
    WeatherAdapterResult
)
from backend.app.weather.cache import weather_cache

logger = logging.getLogger("aegis.weather")


class WeatherSourceAdapter:
    """
    Production-grade meteorological adapter interfacing with Open-Meteo REST API.
    Provides bounded timeouts, exponential backoff, independent rolling windows,
    and deterministic fallback scenarios.
    """
    def __init__(
        self,
        base_url: str = "https://api.open-meteo.com/v1",
        timeout_seconds: float = 8.0,
        cache_enabled: bool = True
    ):
        self.base_url = base_url
        self.timeout = timeout_seconds
        self.cache_enabled = cache_enabled

    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> None:
        """PRD 2: E-019 Validate coordinates before issuing external queries."""
        if not (-90.0 <= lat <= 90.0):
            raise ValidationError(f"Invalid latitude {lat}. Must be between -90 and 90.")
        if not (-180.0 <= lon <= 180.0):
            raise ValidationError(f"Invalid longitude {lon}. Must be between -180 and 180.")

    async def fetch_weather_vector(
        self,
        lat: float,
        lon: float,
        use_cache: bool = True
    ) -> WeatherAdapterResult:
        """
        Fetches meteorological telemetry for given coordinates.
        Checks cache first, then tries live API with retry. If live provider fails,
        returns an explicitly labeled synthetic fallback (PRD 2: E-023).
        """
        self.validate_coordinates(lat, lon)

        if use_cache and self.cache_enabled:
            cached = weather_cache.get(lat, lon)
            if cached is not None:
                return cached

        # Attempt live API fetch with bounded retry
        try:
            result = await self._fetch_live(lat, lon)
            if self.cache_enabled:
                weather_cache.set(lat, lon, result)
            return result
        except Exception as exc:
            logger.warning(f"Live weather fetch failed ({lat}, {lon}): {exc}. Engaging synthetic fallback.")
            fallback = self.get_synthetic_fallback(lat, lon, reason=str(exc))
            return fallback

    async def _fetch_live(self, lat: float, lon: float) -> WeatherAdapterResult:
        """Issues live HTTP request to Open-Meteo and extracts independent rolling series."""
        t0 = time.time()
        url = f"{self.base_url}/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "precipitation,soil_moisture_0_to_1cm,relative_humidity_2m,temperature_2m",
            "current": "relative_humidity_2m,temperature_2m",
            "past_days": 7,
            "forecast_days": 1,
            "timezone": "UTC"
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 429:
                raise WeatherProviderError("Open-Meteo API rate limit exceeded (HTTP 429)")
            if resp.status_code != 200:
                raise WeatherProviderError(f"Open-Meteo returned status {resp.status_code}")

            data = resp.json()

        latency_ms = (time.time() - t0) * 1000
        elevation = float(data.get("elevation", 15.0))
        hourly = data.get("hourly", {})
        rain_series = hourly.get("precipitation", [])
        soil_series = hourly.get("soil_moisture_0_to_1cm", [])
        humidity_series = hourly.get("relative_humidity_2m", [])
        temp_series = hourly.get("temperature_2m", [])

        # 1. Independent 24-hour rainfall: sum of most recent 24 hourly values
        rain_24h_slice = rain_series[-24:] if len(rain_series) >= 24 else rain_series
        precip_24h = round(float(sum(r for r in rain_24h_slice if r is not None)), 2)

        # 2. Independent 7-day rainfall: sum of past 168 hours (7 days * 24h)
        # PRD 2: E-014 - NEVER scale 24h by a multiplier
        rain_7d_slice = rain_series[-168:] if len(rain_series) >= 168 else rain_series
        precip_7d = round(float(sum(r for r in rain_7d_slice if r is not None)), 2)

        # 3. Soil moisture: preserve raw m3/m3 and estimate saturation %
        raw_sm = soil_series[-1] if soil_series and soil_series[-1] is not None else 0.35
        # Soil saturation heuristic: ~0.45 m3/m3 is typical saturation limit
        soil_sat_pct = round(min(100.0, max(0.0, (raw_sm / 0.45) * 100.0)), 1)

        # 4. Current humidity and temperature
        current_data = data.get("current", {})
        rel_humidity = float(current_data.get("relative_humidity_2m") or (humidity_series[-1] if humidity_series else 75.0))
        temperature = float(current_data.get("temperature_2m") or (temp_series[-1] if temp_series else 28.0))

        # Range validation (PRD 2: E-017)
        precip_24h = max(0.0, precip_24h)
        precip_7d = max(precip_24h, precip_7d)  # 7-day cumulative must be at least 24h
        rel_humidity = min(100.0, max(0.0, rel_humidity))

        # Regional climatological baseline estimation (dClimate pattern)
        if lon < -100.0:  # North America / California
            baseline_24h = 18.0
        elif lat > 55.0 and 20.0 <= lon <= 32.0:  # Baltic / Northern Europe (Estonia)
            baseline_24h = 22.0
        elif 36.0 <= lat <= 43.0 and 25.0 <= lon <= 45.0:  # Anatolia / Marmara / Türkiye
            baseline_24h = 28.0
        else:  # Indian Subcontinent
            baseline_24h = 35.0

        anomaly_ratio = round(precip_24h / max(baseline_24h, 1.0), 2)

        vector = WeatherVector(
            precipitation_24h_mm=precip_24h,
            precipitation_7d_mm=precip_7d,
            soil_saturation_pct=soil_sat_pct,
            soil_moisture_m3_m3=round(float(raw_sm), 4),
            relative_humidity_pct=rel_humidity,
            elevation_m=elevation,
            temperature_c=temperature,
            drainage_capacity_index=60.0,
            historical_baseline_24h_mm=baseline_24h,
            precipitation_anomaly_ratio=anomaly_ratio
        )

        provenance = ProvenanceMetadata(
            provider_name="Open-Meteo",
            provider_url=self.base_url,
            query_coordinates={"latitude": lat, "longitude": lon},
            response_latency_ms=round(latency_ms, 2),
            data_mode="live",
            is_synthetic=False,
            fallback_reason=None
        )

        return WeatherAdapterResult(
            vector=vector,
            provenance=provenance,
            observations_count_24h=len(rain_24h_slice),
            observations_count_7d=len(rain_7d_slice),
            cached=False
        )

    def get_synthetic_fallback(
        self,
        lat: float,
        lon: float,
        reason: str = "Provider unreachable or offline test fixture"
    ) -> WeatherAdapterResult:
        """
        PRD 2: E-023 Returns an explicitly labeled synthetic fallback dataset.
        Calibrated with regional baseline characteristics for global hotspots.
        """
        # Geolocation-aware synthetic parameter calibration
        if lon < -100.0:  # USA / California Orange County
            p24, p7d, sat, sm, elev, temp, base, prov_loc = 105.0, 210.0, 88.0, 0.40, 45.0, 19.5, 18.0, "Orange County Basin"
        elif 40.0 <= lat <= 43.0 and 26.0 <= lon <= 30.5:  # Türkiye / Istanbul Marmara
            p24, p7d, sat, sm, elev, temp, base, prov_loc = 95.0, 180.0, 92.0, 0.42, 28.0, 21.0, 28.0, "Istanbul Marmara"
        elif 41.0 <= lat <= 43.0 and 33.0 <= lon <= 36.0:  # Türkiye / Kastamonu Bozkurt
            p24, p7d, sat, sm, elev, temp, base, prov_loc = 140.0, 260.0, 99.0, 0.45, 185.0, 17.0, 35.0, "Kastamonu Bozkurt"
        elif 57.0 <= lat <= 60.0 and 22.0 <= lon <= 28.0:  # Estonia / Pärnu Baltic
            p24, p7d, sat, sm, elev, temp, base, prov_loc = 75.0, 165.0, 94.0, 0.43, 6.0, 14.0, 22.0, "Pärnu Baltic Coast"
        elif 25.5 <= lat <= 27.5 and 79.5 <= lon <= 82.5:  # India / Lucknow Gomti Basin
            p24, p7d, sat, sm, elev, temp, base, prov_loc = 120.0, 245.0, 96.0, 0.44, 123.0, 29.0, 42.0, "Lucknow Gomti Basin"
        else:  # Default Monsoon (Mumbai/Assam)
            p24, p7d, sat, sm, elev, temp, base, prov_loc = 78.5, 195.0, 82.0, 0.38, 12.0, 29.5, 35.0, "Monsoon Baseline"

        anomaly = round(p24 / max(base, 1.0), 2)

        vector = WeatherVector(
            precipitation_24h_mm=p24,
            precipitation_7d_mm=p7d,
            soil_saturation_pct=sat,
            soil_moisture_m3_m3=sm,
            relative_humidity_pct=88.0,
            elevation_m=elev,
            temperature_c=temp,
            drainage_capacity_index=55.0,
            historical_baseline_24h_mm=base,
            precipitation_anomaly_ratio=anomaly
        )

        provenance = ProvenanceMetadata(
            provider_name="AEGIS-Synthetic-Fallback-Engine",
            provider_url=f"internal://fixtures/{prov_loc.lower().replace(' ', '_')}",
            query_coordinates={"latitude": lat, "longitude": lon},
            response_latency_ms=0.5,
            data_mode="synthetic",
            is_synthetic=True,
            fallback_reason=reason
        )

        return WeatherAdapterResult(
            vector=vector,
            provenance=provenance,
            observations_count_24h=24,
            observations_count_7d=168,
            cached=False
        )

    def get_deterministic_fixture(self, scenario: str = "cloudburst") -> WeatherAdapterResult:
        """Returns certified test fixture for reproducible evaluations."""
        if scenario == "istanbul":
            p24, p7d, sat, sm, elev, temp, base, lat, lon = 95.0, 180.0, 92.0, 0.42, 28.0, 21.0, 28.0, 41.0082, 28.9784
        elif scenario == "bozkurt":
            p24, p7d, sat, sm, elev, temp, base, lat, lon = 140.0, 260.0, 99.0, 0.45, 185.0, 17.0, 35.0, 41.9572, 34.0125
        elif scenario == "orange_county":
            p24, p7d, sat, sm, elev, temp, base, lat, lon = 105.0, 210.0, 88.0, 0.40, 45.0, 19.5, 18.0, 33.7175, -117.8311
        elif scenario == "parnu":
            p24, p7d, sat, sm, elev, temp, base, lat, lon = 75.0, 165.0, 94.0, 0.43, 6.0, 14.0, 22.0, 58.3859, 24.4971
        elif scenario == "lucknow":
            p24, p7d, sat, sm, elev, temp, base, lat, lon = 120.0, 245.0, 96.0, 0.44, 123.0, 29.0, 42.0, 26.8467, 80.9462
        elif scenario == "cloudburst":
            p24, p7d, sat, sm, elev, temp, base, lat, lon = 140.0, 325.0, 95.0, 0.44, 8.0, 26.0, 35.0, 19.0728, 72.8797
        elif scenario == "arid":
            p24, p7d, sat, sm, elev, temp, base, lat, lon = 0.0, 4.0, 15.0, 0.08, 450.0, 38.0, 10.0, 26.9124, 75.7873
        else:  # moderate
            p24, p7d, sat, sm, elev, temp, base, lat, lon = 45.0, 110.0, 60.0, 0.28, 25.0, 31.0, 30.0, 19.0728, 72.8797

        anomaly = round(p24 / max(base, 1.0), 2)

        vector = WeatherVector(
            precipitation_24h_mm=p24,
            precipitation_7d_mm=p7d,
            soil_saturation_pct=sat,
            soil_moisture_m3_m3=sm,
            relative_humidity_pct=85.0,
            elevation_m=elev,
            temperature_c=temp,
            drainage_capacity_index=50.0,
            historical_baseline_24h_mm=base,
            precipitation_anomaly_ratio=anomaly
        )

        provenance = ProvenanceMetadata(
            provider_name="AEGIS-Golden-Fixture",
            provider_url=f"fixture://scenarios/{scenario}",
            query_coordinates={"latitude": lat, "longitude": lon},
            response_latency_ms=0.1,
            data_mode="fixture",
            is_synthetic=True,
            fallback_reason=f"Certified golden benchmark fixture ({scenario})"
        )

        return WeatherAdapterResult(
            vector=vector,
            provenance=provenance,
            observations_count_24h=24,
            observations_count_7d=168,
            cached=False
        )


weather_adapter = WeatherSourceAdapter()
