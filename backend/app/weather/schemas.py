"""
Meteorological Data Schemas
Conforms to PRD 2: E-013, E-014, E-015, E-016, E-017, E-018, E-023.
Ensures observed vs forecast separation, explicit units, provenance, and synthetic flags.
"""
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class WeatherObservation(BaseModel):
    """Single meteorological measurement with timestamp, unit, and observation semantics."""
    timestamp_utc: str = Field(..., description="Observation timestamp in ISO-8601 UTC with Z suffix")
    value: float = Field(..., description="Observed numeric value")
    unit: str = Field(..., description="Physical unit (e.g. mm, %, m3/m3, degC, hPa)")
    is_forecast: bool = Field(default=False, description="Whether this value is forecasted vs empirically observed")


class ProvenanceMetadata(BaseModel):
    """Data provenance tracing for independent evidence validation."""
    provider_name: str = Field(default="Open-Meteo", description="Weather service provider")
    provider_url: str = Field(default="https://api.open-meteo.com/v1", description="Provider endpoint")
    query_coordinates: Dict[str, float] = Field(..., description="Normalized queried lat/lon")
    fetch_timestamp_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    response_latency_ms: float = Field(default=0.0)
    data_mode: Literal["live", "fixture", "synthetic"] = Field(default="live")
    fallback_reason: Optional[str] = Field(default=None, description="Reason if synthetic fallback was triggered")
    is_synthetic: bool = Field(default=False)
    attribution: str = Field(default="Weather data from Open-Meteo under CC BY 4.0")


class WeatherVector(BaseModel):
    """6-feature physical hydro-meteorological vector for Agent 1 ML model."""
    precipitation_24h_mm: float = Field(..., ge=0.0, description="Measured sum of past 24 hourly rainfall values")
    precipitation_7d_mm: float = Field(..., ge=0.0, description="Independent measured sum of past 168 hourly rainfall values")
    soil_saturation_pct: float = Field(..., ge=0.0, le=100.0, description="Estimated soil saturation percentage")
    soil_moisture_m3_m3: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Raw volumetric soil moisture fraction")
    relative_humidity_pct: float = Field(..., ge=0.0, le=100.0, description="Measured relative humidity")
    elevation_m: float = Field(..., description="Topographical elevation in meters")
    temperature_c: Optional[float] = Field(default=None, ge=-90.0, le=60.0, description="Current ambient temperature in Celsius")
    drainage_capacity_index: float = Field(default=65.0, ge=0.0, le=100.0)


class WeatherAdapterResult(BaseModel):
    """Complete meteorological adapter output with vector and verifiable provenance."""
    vector: WeatherVector
    provenance: ProvenanceMetadata
    observations_count_24h: int = Field(default=24)
    observations_count_7d: int = Field(default=168)
    cached: bool = Field(default=False)
