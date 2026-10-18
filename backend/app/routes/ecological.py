"""
TERRA-SENTINEL: Sentinel Flood-Watch Ecological Encroachment Router
Phase 30.4: REST API Endpoints for Multi-Temporal Change Detection & Ecological Threat Index (ETI)
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path

from backend.app.ecological_watch import (
    ecological_watch_engine,
    EcologicalScanRequest,
    EcologicalScanResult,
    EcologicalSiteProfile,
    EcologicalThreatTier
)

logger = logging.getLogger("terra_sentinel.routes.ecological")

router = APIRouter(tags=["Sentinel Flood-Watch Ecological Encroachment"])


@router.post("/ecological/scan", response_model=EcologicalScanResult)
async def scan_ecological_threat_post(req: EcologicalScanRequest):
    """
    Executes multi-temporal satellite change detection across sensitive environmental sites:
    Computes Delta_NDBI (concrete built-up), Delta_NDVI (vegetation canopy loss),
    and Delta_MNDWI (wetland shrinkage) to derive the Ecological Threat Index (ETI).
    """
    try:
        return ecological_watch_engine.scan_site(req)
    except Exception as e:
        logger.error(f"Error scanning ecological site {req.site_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ecological scan failure: {str(e)}")


@router.get("/ecological/scan", response_model=EcologicalScanResult)
async def scan_ecological_threat_get(
    site_id: str = Query("site_mithi_mangrove", description="Target site ID: site_mithi_mangrove, site_bellandur_wetland, site_yamuna_oza, site_deepor_beel, site_pallikaranai_marsh"),
    current_ndbi: Optional[float] = Query(None, description="Observed NDBI"),
    current_ndvi: Optional[float] = Query(None, description="Observed NDVI"),
    current_mndwi: Optional[float] = Query(None, description="Observed MNDWI")
):
    """
    Convenience GET endpoint executing multi-temporal ecological threat scan.
    """
    req = EcologicalScanRequest(
        site_id=site_id,
        current_ndbi=current_ndbi,
        current_ndvi=current_ndvi,
        current_mndwi=current_mndwi
    )
    return ecological_watch_engine.scan_site(req)


@router.get("/ecological/sites", response_model=List[EcologicalSiteProfile])
async def list_ecological_sites():
    """
    Returns preloaded catalog of sensitive coastal, wetland, and riverine ecological buffers.
    """
    return ecological_watch_engine.list_sites()


@router.get("/ecological/sites/{site_id}", response_model=EcologicalSiteProfile)
async def get_ecological_site_by_id(
    site_id: str = Path(..., description="Site ID (e.g. site_mithi_mangrove)")
):
    """
    Retrieves site profile including baseline spectral indices, coordinates, and protected legal status.
    """
    site = ecological_watch_engine.get_site(site_id)
    if not site:
        raise HTTPException(status_code=404, detail=f"Ecological site '{site_id}' not found in catalog")
    return site


@router.get("/ecological/threats", response_model=List[EcologicalScanResult])
async def list_active_ecological_threats():
    """
    Returns list of recently detected ecological violations (MODERATE, HIGH, CRITICAL).
    """
    return ecological_watch_engine.get_active_threats()


@router.get("/ecological/spec")
async def get_ecological_specification():
    """
    Returns architectural specifications and governing mathematical invariants for Phase 30.4.
    """
    return {
        "module": "Phase 30.4 Sentinel Flood-Watch Ecological Encroachment & Wetland Threat Engine",
        "governing_invariants": {
            "spectral_indices": {
                "NDBI": "(B11_SWIR1 - B08_NIR) / (B11_SWIR1 + B08_NIR)",
                "MNDWI": "(B03_Green - B11_SWIR1) / (B03_Green + B11_SWIR1)",
                "NDVI": "(B08_NIR - B04_Red) / (B08_NIR + B04_Red)"
            },
            "ecological_threat_index": "ETI = 0.45 * max(0, Delta_NDBI) + 0.35 * max(0, -Delta_NDVI) + 0.20 * max(0, -Delta_MNDWI)",
            "threat_classification": {
                "CRITICAL_ENCROACHMENT": "ETI >= 0.60",
                "HIGH_RISK_CLEARANCE": "0.40 <= ETI < 0.60",
                "MODERATE_ALTERATION": "0.20 <= ETI < 0.40",
                "STABLE_ECOLOGICAL_BUFFER": "ETI < 0.20"
            }
        },
        "supported_sites": [s.site_id for s in ecological_watch_engine.list_sites()],
        "source_repo": "Hou-dini/sentinel-flood-watch"
    }
