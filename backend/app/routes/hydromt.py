"""
AEGIS-CLIMATE: Deltares HydroMT Computational Hydrography Router
Phase 30.2: REST API Endpoints for D8 Watershed Delineation & Topographic Wetness Index (TWI)
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path

from backend.app.hydromt_engine import (
    hydromt_engine,
    DelineateRequest,
    DelineationResult,
    HydroMTBasinProfile,
    LandCoverType
)

logger = logging.getLogger("aegis.routes.hydromt")

router = APIRouter(tags=["Deltares HydroMT Computational Hydrography"])


@router.post("/hydromt/delineate", response_model=DelineationResult)
async def delineate_catchment_post(req: DelineateRequest):
    """
    Executes automated Deltares D8 flow routing, upslope contributing area accumulation,
    and Topographic Wetness Index (TWI) calculation across target watershed grids.
    """
    try:
        return hydromt_engine.delineate_catchment(req)
    except Exception as e:
        logger.error(f"Error delineating catchment for basin {req.basin_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"HydroMT delineation failure: {str(e)}")


@router.get("/hydromt/twi", response_model=DelineationResult)
async def get_catchment_twi(
    basin_id: str = Query("mumbai_mithi", description="Basin ID: mumbai_mithi, bengaluru_vrishabhavathi, delhi_yamuna, assam_brahmaputra, chennai_adyar"),
    grid_size: int = Query(8, ge=4, le=32, description="NxN grid size"),
    cell_resolution_m: float = Query(30.0, ge=5.0, le=500.0, description="Spatial resolution in meters"),
    precip_mm: float = Query(95.0, ge=0.0, description="Precipitation depth in mm"),
    land_cover: LandCoverType = Query(LandCoverType.URBAN_IMPERVIOUS)
):
    """
    Convenience GET endpoint computing Topographic Wetness Index grid and critical depressions.
    """
    req = DelineateRequest(
        basin_id=basin_id,
        grid_size=grid_size,
        cell_resolution_m=cell_resolution_m,
        inflow_precipitation_mm=precip_mm,
        land_cover=land_cover
    )
    return hydromt_engine.delineate_catchment(req)


@router.get("/hydromt/basins", response_model=List[HydroMTBasinProfile])
async def list_hydromt_basins():
    """
    Returns preloaded Indian river basins with baseline topographical elevations and dominant land covers.
    """
    return hydromt_engine.list_basins()


@router.get("/hydromt/basins/{basin_id}", response_model=HydroMTBasinProfile)
async def get_hydromt_basin_by_id(
    basin_id: str = Path(..., description="Basin ID (e.g. mumbai_mithi)")
):
    """
    Retrieves hydrological basin profile including center coordinates, outlet elevation, and total area.
    """
    basin = hydromt_engine.get_basin(basin_id)
    if not basin:
        raise HTTPException(status_code=404, detail=f"Basin {basin_id} not found in catalog")
    return basin


@router.get("/hydromt/spec")
async def get_hydromt_specification():
    """
    Returns architectural specifications and governing mathematical invariants for Phase 30.2.
    """
    return {
        "module": "Phase 30.2 Deltares HydroMT Computational Hydrography Engine",
        "governing_invariants": {
            "topographic_wetness_index": "TWI = ln(alpha / (tan(beta) + 1e-4))",
            "manning_overland_velocity": "v = (1/n) * R_h^(2/3) * S_0^(1/2)",
            "critical_depression_condition": "TWI >= 12.0 marks structural flood pooling sinks"
        },
        "supported_basins": [b.basin_id for b in hydromt_engine.list_basins()],
        "flow_routing_algorithm": "D8 Steepest Descent Routing (ESRI / Deltares Standard)",
        "source_repo": "Deltares/hydromt (wflow, pyflwdir, SFINCS)"
    }
