"""
Unit & Integration Tests for Phase 30.3: Panda Protocol Satellite Algorithmic Carbon MRV Engine
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.panda_carbon_mrv import (
    panda_mrv_engine,
    BiomeType,
    MRVVerificationRequest,
    STOICHIOMETRIC_CO2_RATIO,
    BIOME_KAPPA_FACTORS
)
from mcp_hub.hub import execute_tool_logic, TOOLS_REGISTRY

client = TestClient(app)


def test_mrv_stoichiometric_ratio_invariant():
    """Governing invariant: Stoichiometric ratio must equal molecular weight of CO2 (44) / C (12)."""
    assert abs(STOICHIOMETRIC_CO2_RATIO - (44.0 / 12.0)) < 1e-6
    assert round(STOICHIOMETRIC_CO2_RATIO, 4) == 3.6667


def test_mrv_biome_kappa_factors():
    """Verify biome carbon density parameters for all supported biomes."""
    assert BiomeType.MANGROVE_SPONGE in BIOME_KAPPA_FACTORS
    assert BiomeType.TROPICAL_MOIST_DECIDUOUS in BIOME_KAPPA_FACTORS
    assert BiomeType.URBAN_MIYAWAKI in BIOME_KAPPA_FACTORS
    assert BiomeType.SEMI_ARID_SCRUB in BIOME_KAPPA_FACTORS

    assert BIOME_KAPPA_FACTORS[BiomeType.MANGROVE_SPONGE] == 14.2
    assert BIOME_KAPPA_FACTORS[BiomeType.TROPICAL_MOIST_DECIDUOUS] == 11.5
    assert BIOME_KAPPA_FACTORS[BiomeType.URBAN_MIYAWAKI] == 8.8
    assert BIOME_KAPPA_FACTORS[BiomeType.SEMI_ARID_SCRUB] == 4.2


def test_mrv_biomass_and_co2_calculation():
    """
    Governing invariant:
    Delta_Biomass = A * max(0, Delta_NDVI) * kappa * f_canopy
    Delta_CO2e = Delta_Biomass * (44 / 12)
    """
    area = 100.0  # ha
    delta_ndvi = 0.20
    kappa = 14.2
    canopy = 0.80

    biomass, co2e = panda_mrv_engine.calculate_biomass_and_co2(
        area_ha=area,
        delta_ndvi=delta_ndvi,
        biome_type=BiomeType.MANGROVE_SPONGE,
        canopy_factor=canopy
    )

    expected_biomass = round(100.0 * 0.20 * 14.2 * 0.80, 4)
    expected_co2e = round(expected_biomass * (44.0 / 12.0), 4)

    assert biomass == expected_biomass
    assert co2e == expected_co2e

    # Negative growth should clamp to 0.0 (no negative phantom deductions)
    bio_neg, co2_neg = panda_mrv_engine.calculate_biomass_and_co2(
        area_ha=100.0,
        delta_ndvi=-0.15,
        biome_type=BiomeType.MANGROVE_SPONGE,
        canopy_factor=0.80
    )
    assert bio_neg == 0.0
    assert co2_neg == 0.0


def test_mrv_cryptographic_proof_generation():
    """
    Verify cryptographic hash format (Keccak-256 / SHA-256 hex string with 0x prefix),
    Polygon Amoy tx hash, and IPFS CIDv1 prefix.
    """
    proof_hash, tx_hash, ipfs_cid = panda_mrv_engine.generate_cryptographic_proof(
        project_id="prj_mumbai_mangrove",
        delta_ndvi=0.16,
        delta_biomass=231.84,
        sequestered_co2e=850.08,
        wallet="0x71C8364860D4e0223E4c38AcEbA218175f78235C",
        timestamp="2026-10-18T20:00:00Z"
    )

    assert proof_hash.startswith("0x")
    assert len(proof_hash) == 66
    assert tx_hash.startswith("0x")
    assert len(tx_hash) == 66
    assert ipfs_cid.startswith("bafybeipanda")
    assert ipfs_cid.endswith("mrvv1")


def test_mrv_project_catalog_listing_and_retrieval():
    """Verify registry of preloaded Indian sponge projects."""
    projects = panda_mrv_engine.list_projects()
    assert len(projects) >= 5

    p_ids = [p.project_id for p in projects]
    assert "prj_mumbai_mangrove" in p_ids
    assert "prj_sundarbans_delta" in p_ids
    assert "prj_western_ghats" in p_ids
    assert "prj_delhi_aravali" in p_ids
    assert "prj_bengaluru_lakes" in p_ids

    mumbai_proj = panda_mrv_engine.get_project("prj_mumbai_mangrove")
    assert mumbai_proj is not None
    assert mumbai_proj.state == "Maharashtra"
    assert mumbai_proj.project_area_ha == 120.0
    assert mumbai_proj.biome_type == BiomeType.MANGROVE_SPONGE

    non_existent = panda_mrv_engine.get_project("non_existent_project_id")
    assert non_existent is None


def test_mrv_rest_api_endpoints():
    """Verify FastAPI routes under /api/v1/carbon/mrv/*."""
    # List projects
    r_list = client.get("/api/v1/carbon/mrv/projects")
    assert r_list.status_code == 200
    assert len(r_list.json()) >= 5

    # Get single project
    r_single = client.get("/api/v1/carbon/mrv/projects/prj_sundarbans_delta")
    assert r_single.status_code == 200
    assert r_single.json()["project_name"] == "Sundarbans Biosphere Blue Carbon Reserve"

    # Single project 404
    r_404 = client.get("/api/v1/carbon/mrv/projects/unknown_prj")
    assert r_404.status_code == 404

    # GET MRV Verification
    r_get_v = client.get("/api/v1/carbon/mrv/verify?project_id=prj_mumbai_mangrove")
    assert r_get_v.status_code == 200
    data_get_v = r_get_v.json()
    assert data_get_v["project_id"] == "prj_mumbai_mangrove"
    assert data_get_v["sequestered_co2e_tons"] > 0.0
    assert data_get_v["cryptographic_proof_hash"].startswith("0x")

    # POST MRV Verification
    post_payload = {
        "project_id": "prj_western_ghats",
        "baseline_ndvi": 0.45,
        "current_ndvi": 0.65,
        "canopy_coverage_factor": 0.90,
        "beneficiary_wallet": "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC"
    }
    r_post_v = client.post("/api/v1/carbon/mrv/verify", json=post_payload)
    assert r_post_v.status_code == 200
    data_post_v = r_post_v.json()
    assert data_post_v["delta_ndvi"] == 0.20
    assert data_post_v["beneficiary_wallet"] == "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC"
    assert data_post_v["verification_tier"] == "TIER_1_SENTINEL_2_ALGORITHMIC_PROOF"

    # Specification
    r_spec = client.get("/api/v1/carbon/mrv/spec")
    assert r_spec.status_code == 200
    assert "biomass_growth" in r_spec.json()["governing_invariants"]


def test_mrv_mcp_tool_execution():
    """Verify MCP Tool execution for verify_satellite_carbon_mrv."""
    assert "verify_satellite_carbon_mrv" in TOOLS_REGISTRY

    params = {
        "project_id": "prj_mumbai_mangrove",
        "baseline_ndvi": 0.40,
        "current_ndvi": 0.60,
        "canopy_coverage_factor": 0.85,
        "beneficiary_wallet": "0x71C8364860D4e0223E4c38AcEbA218175f78235C"
    }
    result = execute_tool_logic("verify_satellite_carbon_mrv", params)
    assert result["project_id"] == "prj_mumbai_mangrove"
    assert result["delta_ndvi"] == 0.20
    assert result["delta_biomass_dry_tons"] > 0.0
    assert result["sequestered_co2e_tons"] > 0.0
    assert result["cryptographic_proof_hash"].startswith("0x")
