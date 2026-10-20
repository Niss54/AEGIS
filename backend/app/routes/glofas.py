"""
AEGIS-CLIMATE: Open-Meteo GloFAS River Discharge & Ensemble Forecast Router
Phase 29.1: Copernicus GloFAS LISFLOOD REST API Endpoints
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from backend.app.openmeteo_glofas import (
    glofas_engine,
    GloFASForecastResponse,
    RiverBasinProfile,
    CatchmentSeverityRequest,
    CatchmentSeverityResponse
)

logger = logging.getLogger("aegis.routes.glofas")

router = APIRouter(tags=["Open-Meteo GloFAS Hydrological Forecasting"])


@router.get("/forecast/glofas", response_model=GloFASForecastResponse)
async def get_glofas_river_forecast(
    basin_id: Optional[str] = Query(None, description="Monitored river basin identifier (e.g., mumbai_mithi, assam_brahmaputra)"),
    lat: Optional[float] = Query(None, description="Latitude for nearest basin query"),
    lon: Optional[float] = Query(None, description="Longitude for nearest basin query"),
    forecast_days: int = Query(7, ge=3, le=30, description="Ensemble forecast projection horizon in days")
):
    """
    Retrieves Copernicus GloFAS LISFLOOD daily river discharge (m³/s) forecast,
    statistical return-period classification, and ensemble hydrograph.
    """
    try:
        return glofas_engine.get_forecast(basin_id=basin_id, lat=lat, lon=lon, forecast_days=forecast_days)
    except Exception as e:
        logger.error(f"Error computing GloFAS forecast: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Hydrological forecast computation error: {str(e)}")


@router.get("/forecast/glofas/basins", response_model=List[RiverBasinProfile])
async def list_glofas_monitored_basins():
    """
    Returns catalogue of high-risk Indian river basins monitored by GloFAS
    along with their baseline flows and return-period thresholds.
    """
    return glofas_engine.list_basins()


@router.post("/forecast/glofas/catchment-severity", response_model=CatchmentSeverityResponse)
async def compute_composite_catchment_severity(req: CatchmentSeverityRequest):
    """
    Computes a composite Catchment Inundation Severity Index fusing
    surface stormwater runoff with GloFAS river channel discharge.
    """
    try:
        return glofas_engine.compute_catchment_severity(req)
    except Exception as e:
        logger.error(f"Error computing catchment severity: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Catchment severity computation error: {str(e)}")


@router.get("/forecast/glofas/spec")
async def get_glofas_specification():
    """
    Returns architectural specifications and governing mathematical invariants
    for the Copernicus GloFAS LISFLOOD forecast engine.
    """
    return {
        "engine": "Copernicus GloFAS v4.0 LISFLOOD",
        "governing_invariants": {
            "channel_routing": "Q(t) = Q_base + integral(R(tau) * U(t - tau) dtau)",
            "elevation_downscaling": "T(z) = T_model - 0.0065 * (z_SRTM - z_model)",
            "composite_severity": "Severity = clamp(0.55 * (Q / Q20) + 0.45 * (Runoff / 75mm), 0.0, 1.0)"
        },
        "return_periods": {
            "Q2": "2-Year Flood (Mean Annual Flood)",
            "Q5": "5-Year Moderate Inundation",
            "Q20": "20-Year Catastrophic Inundation"
        },
        "monitored_basins_count": len(glofas_engine.basins)
    }
