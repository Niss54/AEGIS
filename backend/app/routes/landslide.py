"""
AEGIS-CLIMATE: SailabAlert Multi-Hazard Landslide Coupling & Trilingual Advisory Router
Phase 30.1: REST API Endpoints for Compound Slope & Flood Hazard Assessment
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path

from backend.app.sailab_landslide import (
    sailab_engine,
    HazardTier,
    MonitoringStation,
    LandslidePredictRequest,
    LandslidePredictionResult,
    BilingualAdvisoryRequest
)

logger = logging.getLogger("aegis.routes.landslide")

router = APIRouter(tags=["Multi-Hazard Landslide & SailabAlert Intelligence"])


@router.post("/hazard/landslide-predict", response_model=LandslidePredictionResult)
async def predict_landslide_hazard(req: LandslidePredictRequest):
    """
    Computes the Compound Flood & Landslide Susceptibility Index (CFLSI)
    coupling 24h rainfall, river stage, soil saturation percentage, and 30m SRTM DEM slope angle.
    Returns trilingual public safety advisories across English, Urdu (اردو), and Hindi (देवनागरी).
    """
    try:
        return sailab_engine.predict_hazard(req)
    except Exception as e:
        logger.error(f"Error computing compound hazard prediction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Hazard calculation failure: {str(e)}")


@router.get("/hazard/stations", response_model=List[MonitoringStation])
async def list_monitoring_stations(
    country: Optional[str] = Query(None, description="Filter by country: India, Pakistan")
):
    """
    Returns monitored high-risk multi-hazard mountain and river stations across Bharat & vulnerable global corridors.
    """
    stations = sailab_engine.get_stations()
    if country:
        c_clean = country.strip().lower()
        return [s for s in stations if s.country.lower() == c_clean]
    return stations


@router.get("/hazard/stations/{station_id}", response_model=MonitoringStation)
async def get_station_by_id(
    station_id: str = Path(..., description="Station ID (e.g. STN-WGHAT-01)")
):
    """
    Retrieves baseline topographical slope and danger water stages for a specific station.
    """
    station = sailab_engine.get_station(station_id)
    if not station:
        raise HTTPException(status_code=404, detail=f"Station {station_id} not found")
    return station


@router.post("/hazard/advisory")
async def generate_trilingual_advisory(req: BilingualAdvisoryRequest):
    """
    Generates context-specific, plain-language public safety advisories in English, Urdu, and Hindi.
    """
    adv_en, adv_ur, adv_hi, active_tier = sailab_engine._generate_trilingual_advisories(
        tier=req.hazard_tier,
        location=req.location_name,
        rainfall=req.rainfall_mm,
        slope=req.slope_deg,
        soil=req.soil_moisture_pct
    )
    return {
        "hazard_tier": req.hazard_tier,
        "location": req.location_name,
        "advisory_english": adv_en,
        "advisory_urdu": adv_ur,
        "advisory_hindi": adv_hi,
        "circuit_tier": active_tier
    }


@router.get("/hazard/spec")
async def get_landslide_specification():
    """
    Returns architectural specifications and governing mathematical invariants for Phase 30.1.
    """
    return {
        "module": "Phase 30.1 SailabAlert Multi-Hazard Landslide Coupling",
        "governing_invariant": "CFLSI = 0.35*(R/150) + 0.25*(S/100) + 0.25*sin(theta) + 0.15*(H/7.0)",
        "catastrophic_override": "IF slope > 35° AND soil > 85% AND rain > 100mm -> CATASTROPHIC Landslide Alert",
        "supported_languages": ["English", "Urdu (اردو)", "Hindi (देवनागरी)"],
        "cloud_llm_model": "Groq Qwen 3.8 27B / Llama 3.3 70B",
        "fallback_tier": "Deterministic localized template engine (sub-50ms SLA)",
        "monitored_stations_count": len(sailab_engine.get_stations())
    }
