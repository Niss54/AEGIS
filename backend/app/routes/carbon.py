"""
TERRA-SENTINEL: Toucan Protocol Web3 Carbon Resilience Router
Phase 29.4: Toucan Carbon Bridge & Retirement REST API Endpoints
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException, Path
from backend.app.toucan_bridge import (
    toucan_engine,
    RetirementCertificate,
    RetirementRequest,
    AutoOffsetRequest,
    CarbonProject,
    CarbonPool
)

logger = logging.getLogger("terra_sentinel.routes.carbon")

router = APIRouter(tags=["Toucan Protocol Carbon Resilience & Retirement"])


@router.post("/carbon/retire", response_model=RetirementCertificate)
async def retire_carbon_credits(req: RetirementRequest):
    """
    Executes permanent on-chain carbon retirement for BCT/NCT/TCO2 credits on Polygon Amoy.
    Generates deterministic Keccak-256 certificate hash and IPFS CIDv1 metadata.
    """
    try:
        return toucan_engine.retire_carbon_credits(req)
    except Exception as e:
        logger.error(f"Error retiring carbon credits: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Carbon retirement error: {str(e)}")


@router.post("/carbon/auto-offset", response_model=RetirementCertificate)
async def auto_offset_flood_var(req: AutoOffsetRequest):
    """
    1-Click Auto-Offset Helper:
    Automatically calculates required carbon tons to neutralize target flood VaR ($USD)
    and executes atomic on-chain retirement against nature-based bio-shield projects.
    """
    try:
        return toucan_engine.auto_offset_by_var(req)
    except Exception as e:
        logger.error(f"Error executing auto-offset: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Auto-offset error: {str(e)}")


@router.get("/carbon/certificates", response_model=List[RetirementCertificate])
async def list_retirement_certificates(
    limit: int = Query(50, ge=1, le=200, description="Max certificates to return")
):
    """
    Returns list of verified on-chain retirement certificates for corporate ESG reporting.
    """
    return toucan_engine.list_certificates(limit=limit)


@router.get("/carbon/certificates/{cert_id}", response_model=RetirementCertificate)
async def get_retirement_certificate_by_id(
    cert_id: str = Path(..., description="Unique certificate identifier (e.g. TOUCAN-CERT-001)")
):
    """
    Retrieves full cryptographic retirement certificate by ID.
    """
    cert = toucan_engine.get_certificate(cert_id)
    if not cert:
        raise HTTPException(status_code=404, detail=f"Certificate {cert_id} not found")
    return cert


@router.get("/carbon/projects", response_model=List[CarbonProject])
async def list_carbon_projects(
    pool: Optional[CarbonPool] = Query(None, description="Filter by carbon pool (BCT, NCT, TCO2)")
):
    """
    Returns catalogue of verified carbon offset projects providing physical flood bio-shield protection.
    """
    return toucan_engine.list_projects(pool=pool)


@router.get("/carbon/pools")
async def list_carbon_pools():
    """Returns available Toucan on-chain carbon pools (NCT, BCT)."""
    return [
        {
            "pool_name": "Nature Carbon Tonne",
            "token_symbol": "NCT",
            "polygon_address": "0x7BE59100075723ba251432661De6ab1A51581224",
            "balance_tco2": 24250.0,
            "avoided_flood_var_per_ton_usd": 450.0,
            "description": "Nature-based NBS flood buffer credits: Sundarbans Mangrove Blue Carbon & Mithi Sponge Wetlands.",
            "supported_methodologies": ["VCS-1422 (Blue Carbon)", "VCS-2104 (Wetland Restoration)", "GS-4421 (Riparian Buffer)"]
        },
        {
            "pool_name": "Base Carbon Tonne",
            "token_symbol": "BCT",
            "polygon_address": "0x2F800Db0fdb5223b3C3f354886d907A671414A7F",
            "balance_tco2": 18250.0,
            "avoided_flood_var_per_ton_usd": 380.0,
            "description": "Standard Verified Carbon Standard (VCS) vintage verified carbon tonnes for municipal climate resilience.",
            "supported_methodologies": ["VCS-VM0007 (REDD+)", "VCS-VM0010 (Afforestation)"]
        }
    ]


@router.get("/carbon/registry", response_model=List[RetirementCertificate])
async def list_carbon_registry(limit: int = Query(50, ge=1, le=200)):
    """Alias for /carbon/certificates returning all on-chain retirement certificates."""
    return toucan_engine.list_certificates(limit=limit)


@router.get("/carbon/spec")
async def get_toucan_bridge_specification():
    """
    Returns architectural specifications and cryptographic invariants for Toucan Carbon Bridge.
    """
    return {
        "protocol": "Toucan Protocol Web3 Carbon Bridge (TypeScript SDK Synthesis)",
        "chain": "Polygon Amoy Testnet (Chain ID: 80002)",
        "supported_pools": ["BCT", "NCT", "TCO2"],
        "governing_invariant": "CertHash = keccak256(Beneficiary || TCO2Address || AmountWei || AvoidedVaR || BlockNumber)",
        "regulatory_compliance": "SEBI BRSR Principle 6 (India ESG Net-Zero Mandate)",
        "active_certificates_count": len(toucan_engine._certificates),
        "active_projects_count": len(toucan_engine._projects)
    }
