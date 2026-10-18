"""
Unit & Integration Test Suite for Phase 29.4:
Toucan Protocol Web3 Carbon Resilience Bridge & Retirement Registry
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.toucan_bridge import (
    toucan_engine,
    RetirementRequest,
    AutoOffsetRequest,
    CarbonPool
)

client = TestClient(app)


def test_toucan_seeded_projects_and_pools():
    """Validates that verified carbon offset projects are present across NCT and BCT pools."""
    projects = toucan_engine.list_projects()
    assert len(projects) >= 4

    prj_ids = [p.project_id for p in projects]
    assert "PRJ-SUNDARBANS-01" in prj_ids
    assert "PRJ-MITHI-02" in prj_ids
    assert "PRJ-ENNORE-03" in prj_ids
    assert "PRJ-SOLAR-04" in prj_ids

    # Sundarbans Mangrove Bio-Shield must be NCT pool with high avoided VaR rate
    sundarbans = toucan_engine.get_project("PRJ-SUNDARBANS-01")
    assert sundarbans is not None
    assert sundarbans.pool == CarbonPool.NCT
    assert sundarbans.avoided_var_usd_per_ton >= 400.0
    assert sundarbans.tco2_address.startswith("0x")


def test_toucan_seeded_certificate_presence():
    """Verifies that the pre-seeded on-chain retirement certificate exists and meets SEBI BRSR standards."""
    certs = toucan_engine.list_certificates()
    assert len(certs) >= 1

    cert1 = toucan_engine.get_certificate("TOUCAN-CERT-001")
    assert cert1 is not None
    assert cert1.beneficiary_name == "Mahindra Lifespaces Developers"
    assert cert1.certificate_hash.startswith("0x")
    assert len(cert1.certificate_hash) == 66  # 32 bytes hex + '0x'
    assert cert1.polygon_tx_hash.startswith("0x")
    assert cert1.ipfs_cid.startswith("bafybei")
    assert cert1.sebi_brsr_compliant is True


def test_toucan_retire_carbon_credits_flow():
    """
    Validates on-chain carbon retirement flow:
    Tons -> Avoided VaR -> Keccak256 hash -> Polygon tx hash -> IPFS CIDv1.
    """
    req = RetirementRequest(
        beneficiary_name="Infosys Environmental Solutions",
        beneficiary_wallet="0x89205A3A3b2A69De6Dbf7f01ED13B2108B2c43e7",
        pool=CarbonPool.NCT,
        tons_to_retire=75.0,
        project_id="PRJ-SUNDARBANS-01",
        retirement_reason="Corporate Scope 1 Emissions Offset & Coastal Sponge Defense"
    )

    cert = toucan_engine.retire_carbon_credits(req)
    assert cert.certificate_id.startswith("TOUCAN-CERT-")
    assert cert.tons_retired == 75.0
    assert cert.beneficiary_name == "Infosys Environmental Solutions"
    # Avoided VaR = 75.0 * $450 = $33,750
    assert cert.avoided_flood_var_usd == 33750.0
    assert cert.avoided_flood_var_inr_cr > 0.0
    assert cert.certificate_hash.startswith("0x")
    assert len(cert.certificate_hash) == 66
    assert cert.polygon_tx_hash.startswith("0x")
    assert cert.ipfs_cid.startswith("bafybei")
    assert cert.sebi_brsr_compliant is True


def test_toucan_auto_offset_helper():
    """
    Validates 1-Click Auto-Offset Helper:
    Tons = TargetVaR / AvoidedVaR_Per_Ton
    $45,000 / $450 = 100.0 tons retired.
    """
    auto_req = AutoOffsetRequest(
        corporate_name="HDFC Ergo General Insurance",
        target_mitigation_var_usd=45000.0,
        beneficiary_wallet="0x1234567890123456789012345678901234567890",
        pool=CarbonPool.NCT
    )
    cert = toucan_engine.auto_offset_by_var(auto_req)
    assert cert.tons_retired == 100.0
    assert cert.avoided_flood_var_usd == 45000.0
    assert cert.beneficiary_name == "HDFC Ergo General Insurance"


def test_toucan_rest_api_endpoints():
    """Tests all FastAPI REST endpoints for Phase 29.4."""
    # 1. POST /api/v1/carbon/retire
    retire_payload = {
        "beneficiary_name": "Larsen & Toubro Infrastructure",
        "beneficiary_wallet": "0xfe9e8709d3215310075d67e3ed32a380ccf451c8",
        "pool": "NCT",
        "tons_to_retire": 200.0,
        "project_id": "PRJ-MITHI-02",
        "retirement_reason": "Mithi River Basin Urban Sponge Wetland Mitigation"
    }
    r_retire = client.post("/api/v1/carbon/retire", json=retire_payload)
    assert r_retire.status_code == 200
    data_cert = r_retire.json()
    new_cert_id = data_cert["certificate_id"]
    assert new_cert_id.startswith("TOUCAN-CERT-")
    assert data_cert["avoided_flood_var_usd"] == 200.0 * 380.0

    # 2. POST /api/v1/carbon/auto-offset
    auto_payload = {
        "corporate_name": "Adani Ports & SEZ Ltd",
        "target_mitigation_var_usd": 22500.0,
        "beneficiary_wallet": "0xab5801a7d398351b8be11c439e05c5b3259aec9b",
        "pool": "NCT"
    }
    r_auto = client.post("/api/v1/carbon/auto-offset", json=auto_payload)
    assert r_auto.status_code == 200
    assert r_auto.json()["tons_retired"] == 50.0  # $22,500 / $450 = 50 tons

    # 3. GET /api/v1/carbon/certificates
    r_certs = client.get("/api/v1/carbon/certificates?limit=10")
    assert r_certs.status_code == 200
    c_list = r_certs.json()
    assert isinstance(c_list, list)
    assert len(c_list) >= 3

    # 4. GET /api/v1/carbon/certificates/{cert_id}
    r_get = client.get(f"/api/v1/carbon/certificates/{new_cert_id}")
    assert r_get.status_code == 200
    assert r_get.json()["certificate_id"] == new_cert_id

    # 5. GET /api/v1/carbon/projects
    r_prj = client.get("/api/v1/carbon/projects?pool=NCT")
    assert r_prj.status_code == 200
    prj_list = r_prj.json()
    assert isinstance(prj_list, list)
    assert len(prj_list) >= 3

    # 6. GET /api/v1/carbon/spec
    r_spec = client.get("/api/v1/carbon/spec")
    assert r_spec.status_code == 200
    assert "governing_invariant" in r_spec.json()
    assert "Polygon Amoy" in r_spec.json()["chain"]


def test_toucan_certificate_not_found_handling():
    """Tests 404 response on non-existent certificate query."""
    r = client.get("/api/v1/carbon/certificates/TOUCAN-CERT-NONEXISTENT-999")
    assert r.status_code == 404
