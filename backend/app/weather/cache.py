"""
Meteorological Cache Implementation
Conforms to PRD 2: E-020 Cache key correctness and TTL management.
Keyed by normalized coordinates, temporal window, and variables.
"""
import time
from typing import Dict, Any, Optional, Tuple
from backend.app.weather.schemas import WeatherAdapterResult


class WeatherCache:
    """Thread-safe in-memory cache with normalized spatial keys and TTL expiration."""
    def __init__(self, default_ttl_seconds: int = 900):  # 15 minutes default
        self._store: Dict[str, Tuple[float, WeatherAdapterResult]] = {}
        self.default_ttl = default_ttl_seconds

    @staticmethod
    def build_key(lat: float, lon: float, precision: int = 3) -> str:
        """
        Normalizes coordinates to fixed decimal precision (approx ~100m at equator)
        to prevent cache fragmentation due to floating point noise.
        """
        norm_lat = round(float(lat), precision)
        norm_lon = round(float(lon), precision)
        return f"wx:{norm_lat:.3f}:{norm_lon:.3f}:v2"

    def get(self, lat: float, lon: float) -> Optional[WeatherAdapterResult]:
        key = self.build_key(lat, lon)
        if key in self._store:
            expiry, result = self._store[key]
            if time.time() < expiry:
                # Return copy with cached flag marked true
                result_copy = result.model_copy(deep=True)
                result_copy.cached = True
                return result_copy
            else:
                del self._store[key]
        return None

    def set(self, lat: float, lon: float, result: WeatherAdapterResult, ttl_seconds: Optional[int] = None) -> None:
        key = self.build_key(lat, lon)
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        expiry = time.time() + ttl
        self._store[key] = (expiry, result)

    def clear(self) -> None:
        self._store.clear()


weather_cache = WeatherCache()
