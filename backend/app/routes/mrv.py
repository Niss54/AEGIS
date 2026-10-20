"""
AEGIS-CLIMATE: Panda Protocol Satellite Algorithmic Carbon MRV Router
Phase 30.3: REST API Endpoints for Remote Sensing Biomass Quantification & Verification Proofs
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path

from backend.app.panda_carbon_mrv import (
    panda_mrv_engine,
    MRVVerificationRequest,
    CarbonMRVProject,
    CarbonMRVVerificationResult,
    STOICHIOMETRIC_CO2_RATIO,
    BIOME_KAPPA_FACTORS
)

logger = logging.getLogger("aegis.routes.mrv")

router = APIRouter(tags=["Panda Protocol Satellite Carbon MRV"])


@router.post("/carbon/mrv/verify", response_model=CarbonMRVVerificationResult)
async def verify_carbon_mrv_post(req: MRVVerificationRequest):
    """
    Executes algorithmic satellite MRV verification:
    Computes Delta_NDVI from Sentinel-2 MSI bands, calculates dry biomass growth,
    derives stoichiometric sequestered tCO2e, and emits cryptographic verification proof.
    """
    try:
        return panda_mrv_engine.verify_carbon_mrv(req)
    except Exception as e:
        logger.error(f"Error executing carbon MRV verification: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Carbon MRV verification failure: {str(e)}")


@router.get("/carbon/mrv/verify", response_model=CarbonMRVVerificationResult)
async def verify_carbon_mrv_get(
    project_id: str = Query("prj_mumbai_mangrove", description="Registered MRV project ID"),
    baseline_ndvi: Optional[float] = Query(None, description="Baseline NDVI"),
    current_ndvi: Optional[float] = Query(None, description="Current Sentinel-2 NDVI"),
    canopy_coverage: Optional[float] = Query(None, description="Canopy fraction [0.0, 1.0]"),
    wallet: str = Query("0x71C8364860D4e0223E4c38AcEbA218175f78235C", description="Beneficiary EVM wallet")
):
    """
    Convenience GET endpoint executing satellite carbon MRV calculation.
    """
    req = MRVVerificationRequest(
        project_id=project_id,
        baseline_ndvi=baseline_ndvi,
        current_ndvi=current_ndvi,
        canopy_coverage_factor=canopy_coverage,
        beneficiary_wallet=wallet
    )
    return panda_mrv_engine.verify_carbon_mrv(req)


@router.get("/carbon/mrv/projects", response_model=List[CarbonMRVProject])
async def list_mrv_projects():
    """
    Returns list of all active nature-based sponge carbon projects monitored by Sentinel-2.
    """
    return panda_mrv_engine.list_projects()


@router.get("/carbon/mrv/projects/{project_id}", response_model=CarbonMRVProject)
async def get_mrv_project_by_id(
    project_id: str = Path(..., description="Project identifier (e.g. prj_mumbai_mangrove)")
):
    """
    Retrieves project metadata, geographical coordinates, and total minted carbon tokens.
    """
    proj = panda_mrv_engine.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found in MRV catalog")
    return proj


@router.get("/carbon/mrv/spec")
async def get_mrv_specification():
    """
    Returns mathematical invariants, stoichiometric ratios, and biome kappa factors for Phase 30.3.
    """
    return {
        "module": "Phase 30.3 Panda Protocol Satellite Algorithmic Carbon MRV Engine",
        "stoichiometric_ratio_co2_to_c": f"44 / 12 = {STOICHIOMETRIC_CO2_RATIO:.5f}",
        "governing_invariants": {
            "biomass_growth": "Delta_Biomass = A * max(0, Delta_NDVI) * kappa_biome * f_canopy",
            "sequestered_co2": "Delta_CO2e = Delta_Biomass * (44 / 12)",
            "cryptographic_proof": "proof_hash = Keccak-256(project_id || Delta_NDVI || Delta_Biomass || sequestered_co2e || wallet || timestamp)"
        },
        "biome_kappa_factors": {k.value: v for k, v in BIOME_KAPPA_FACTORS.items()},
        "supported_projects": [p.project_id for p in panda_mrv_engine.list_projects()],
        "source_repo": "karanjaxyz/panda"
    }
