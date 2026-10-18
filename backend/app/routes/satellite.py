"""
TERRA-SENTINEL Satellite & Earth Observation REST Router
Provides endpoints for Copernicus Sentinel-2 MSI, ISRO Bhuvan NRSC, Google Earth Engine DEM,
and Gemini 2.0 Flash Multimodal Spatial Reasoning.
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field

from backend.app.satellite import (
    earth_observation_engine,
    earth_observation_controller,
    SatelliteObservationModel,
    compute_spectral_indices
)

router = APIRouter(prefix="/satellite", tags=["Earth Observation & Satellite Ingestion"])



class SatelliteIngestRequest(BaseModel):
    lat: float = Field(..., description="Latitude coordinate", json_schema_extra={"example": 19.0728})
    lon: float = Field(..., description="Longitude coordinate", json_schema_extra={"example": 72.8797})
    location_name: str = Field("Mumbai Mithi River", description="Geographic identifier", json_schema_extra={"example": "Mumbai Mithi River Basin"})
    elevation_m: float = Field(12.0, description="Surface elevation in meters")


class MultimodalAnalysisRequest(BaseModel):
    lat: float = Field(..., json_schema_extra={"example": 19.0728})
    lon: float = Field(..., json_schema_extra={"example": 72.8797})
    location_name: str = Field("Mumbai Mithi River Basin", json_schema_extra={"example": "Mumbai Mithi River Basin"})
    waterlogging_depth_cm: int = Field(85, json_schema_extra={"example": 85})
    weather_summary: str = Field("High-intensity monsoon cloudburst, 120mm in 4h", json_schema_extra={"example": "High-intensity monsoon cloudburst"})


@router.post("/ingest")
async def ingest_satellite_telemetry(req: SatelliteIngestRequest):
    """
    Ingests Copernicus Sentinel-2 MSI multispectral indices (NDWI, NDVI, MNDWI),
    ISRO Bhuvan basin geology, and Google Earth Engine NASA SRTM 30m DEM.
    """
    sentinel2_data = earth_observation_engine.get_sentinel2_metadata(req.lat, req.lon)
    bhuvan_data = earth_observation_engine.get_isro_bhuvan_geology(req.lat, req.lon)
    gee_dem = earth_observation_engine.get_google_earth_engine_dem(req.lat, req.lon, req.elevation_m)

    return {
        "status": "success",
        "location": req.location_name,
        "coordinates": {"lat": req.lat, "lon": req.lon},
        "copernicus_sentinel2": sentinel2_data,
        "isro_bhuvan": bhuvan_data,
        "google_earth_engine_dem": gee_dem
    }


@router.post("/analyze-multimodal")
async def analyze_satellite_multimodal(req: MultimodalAnalysisRequest):
    """
    Executes Google Vertex AI Gemini 2.0 Flash Multimodal Spatial Reasoning
    over satellite multispectral rasters, DEM slope gradients, and inundation contours.
    """
    result = earth_observation_engine.analyze_satellite_multimodal(
        lat=req.lat,
        lon=req.lon,
        location_name=req.location_name,
        depth_cm=req.waterlogging_depth_cm,
        weather_summary=req.weather_summary
    )
    return result


@router.get("/layers/{hotspot_id}")
async def get_satellite_contour_layer(
    hotspot_id: str,
    lat: float = Query(19.0728),
    lon: float = Query(72.8797),
    depth_cm: int = Query(75)
):
    """
    Generates dynamic GeoJSON FeatureCollection of Copernicus NDWI flood masks
    and Google Earth Engine SRTM elevation centroids for Leaflet mapping.
    """
    geojson = earth_observation_engine.generate_multispectral_geojson(lat, lon, depth_cm)
    return geojson


# ─── PHASE 16 MULTIMODAL EARTH OBSERVATION PIPELINE ─────────────────────────

class SpectralIndicesRequest(BaseModel):
    green: float = Field(..., ge=0.0, le=1.0, description="Sentinel-2 B03 Green band reflectance", json_schema_extra={"example": 0.28})
    red: float = Field(..., ge=0.0, le=1.0, description="Sentinel-2 B04 Red band reflectance", json_schema_extra={"example": 0.18})
    nir: float = Field(..., ge=0.0, le=1.0, description="Sentinel-2 B08 NIR band reflectance", json_schema_extra={"example": 0.08})
    swir: Optional[float] = Field(None, ge=0.0, le=1.0, description="Optional Sentinel-2 B11 SWIR band reflectance", json_schema_extra={"example": 0.06})


@router.post("/indices/compute")
async def compute_indices_endpoint(req: SpectralIndicesRequest):
    """
    Computes Phase 16 governing mathematical invariants:
    NDWI = (Green - NIR) / (Green + NIR), NDVI = (NIR - Red) / (NIR + Red)
    """
    return compute_spectral_indices(
        green=req.green,
        red=req.red,
        nir=req.nir,
        swir=req.swir
    )


@router.get("/phase16/health")
async def get_earth_observation_health():
    """
    Returns Phase 16 Multimodal Earth Observation health and circuit breaker status.
    """
    return earth_observation_controller.get_health()


@router.post("/phase16/pipeline", response_model=SatelliteObservationModel)
async def execute_phase16_pipeline(payload: Dict[str, Any]):
    """
    Executes PRD Phase 16 Operational Pipeline and returns SatelliteObservationModel.
    """
    try:
        return await earth_observation_controller.execute_phase_pipeline(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

