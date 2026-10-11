"""
AEGIS Meteorological Source Adapter Package
Conforms to PRD 2: E-013 through E-024.
"""
from backend.app.weather.schemas import WeatherObservation, WeatherVector, WeatherAdapterResult, ProvenanceMetadata
from backend.app.weather.adapter import WeatherSourceAdapter, weather_adapter

__all__ = [
    "WeatherObservation",
    "WeatherVector",
    "WeatherAdapterResult",
    "ProvenanceMetadata",
    "WeatherSourceAdapter",
    "weather_adapter"
]
