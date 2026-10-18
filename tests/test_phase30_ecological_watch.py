"""
Unit & Integration Tests for Phase 30.4: Sentinel Flood-Watch Ecological Encroachment & Wetland Threat Engine
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.ecological_watch import (
    ecological_watch_engine,
    EcologicalThreatTier,
    EcologicalSiteCategory,
    EcologicalScanRequest
)
from mcp_hub.hub import execute_tool_logic, TOOLS_REGISTRY

client = TestClient(app)


def test_eti_mathematical_bounds_and_formula():
    """
    Governing invariant:
    ETI = 0.45 * max(0, Delta_NDBI) + 0.35 * max(0, -Delta_NDVI) + 0.20 * max(0, -Delta_MNDWI)
    Bounded in [0.0, 1.0].
    """
    # Baseline stable: zero changes
    eti_zero = ecological_watch_engine.calculate_eti(
        delta_ndbi=0.0,
        delta_ndvi=0.0,
        delta_mndwi=0.0
    )
    assert eti_zero == 0.0

    # Beneficial ecological growth (more green, more water, negative NDBI) should yield 0.0
    eti_positive = ecological_watch_engine.calculate_eti(
        delta_ndbi=-0.25,
        delta_ndvi=0.30,
        delta_mndwi=0.20
    )
    assert eti_positive == 0.0

    # Extreme severe destruction: max changes
    eti_max = ecological_watch_engine.calculate_eti(
        delta_ndbi=1.0,
        delta_ndvi=-1.0,
        delta_mndwi=-1.0
    )
    assert eti_max == 1.0  # 0.45(1.0) + 0.35(1.0) + 0.20(1.0) = 1.00


def test_eti_threat_tier_classification():
    """Verify tier classification based on ETI score thresholds."""
    # Stable: ETI < 0.20
    tier_s, rec_s = ecological_watch_engine.classify_threat_tier(0.12)
    assert tier_s == EcologicalThreatTier.STABLE_ECOLOGICAL_BUFFER
    assert "NORMAL" in rec_s

    # Moderate: 0.20 <= ETI < 0.40
    tier_m, rec_m = ecological_watch_engine.classify_threat_tier(0.28)
    assert tier_m == EcologicalThreatTier.MODERATE_ALTERATION
    assert "ELEVATED" in rec_m

    # High: 0.40 <= ETI < 0.60
    tier_h, rec_h = ecological_watch_engine.classify_threat_tier(0.48)
    assert tier_h == EcologicalThreatTier.HIGH_RISK_CLEARANCE
    assert "HIGH" in rec_h

    # Critical: ETI >= 0.60
    tier_c, rec_c = ecological_watch_engine.classify_threat_tier(0.75)
    assert tier_c == EcologicalThreatTier.CRITICAL_ENCROACHMENT
    assert "URGENT" in rec_c


def test_concrete_and_wetland_change_flags():
    """Verify detection boolean flags when concrete expands or wetland shrinks."""
    req_critical = EcologicalScanRequest(
        site_id="site_mithi_mangrove",
        current_ndbi=0.65,   # baseline is -0.15 -> delta +0.80 -> 0.45 * 0.80 = 0.360
        current_ndvi=-0.10,  # baseline is 0.62 -> delta -0.72 -> 0.35 * 0.72 = 0.252
        current_mndwi=-0.15  # baseline is 0.35 -> delta -0.50 -> 0.20 * 0.50 = 0.100 (Total ETI = 0.712)
    )
    res = ecological_watch_engine.scan_site(req_critical)

    assert res.concrete_expansion_detected is True
    assert res.vegetation_loss_detected is True
    assert res.wetland_shrinkage_detected is True
    assert res.threat_tier == EcologicalThreatTier.CRITICAL_ENCROACHMENT
    assert res.eti_score >= 0.60


def test_ecological_sites_catalog_and_retrieval():
    """Verify preloaded sensitive environmental zones catalog."""
    sites = ecological_watch_engine.list_sites()
    assert len(sites) >= 5

    s_ids = [s.site_id for s in sites]
    assert "site_mithi_mangrove" in s_ids
    assert "site_bellandur_wetland" in s_ids
    assert "site_yamuna_oza" in s_ids
    assert "site_deepor_beel" in s_ids
    assert "site_pallikaranai_marsh" in s_ids

    mithi = ecological_watch_engine.get_site("site_mithi_mangrove")
    assert mithi is not None
    assert mithi.category == EcologicalSiteCategory.MANGROVE_CRZ
    assert "CRZ-1A" in mithi.protected_status

    unknown = ecological_watch_engine.get_site("non_existent_site")
    assert unknown is None


def test_active_threats_history_buffer():
    """Verify elevated threats are recorded in active violation history."""
    req = EcologicalScanRequest(
        site_id="site_bellandur_wetland",
        current_ndbi=0.30,
        current_ndvi=0.20,
        current_mndwi=0.10
    )
    res = ecological_watch_engine.scan_site(req)

    threats = ecological_watch_engine.get_active_threats()
    assert len(threats) > 0
    assert any(t.site_id == "site_bellandur_wetland" for t in threats)


def test_ecological_rest_api_endpoints():
    """Verify FastAPI routes under /api/v1/ecological/*."""
    # List sites
    r_list = client.get("/api/v1/ecological/sites")
    assert r_list.status_code == 200
    assert len(r_list.json()) >= 5

    # Get single site
    r_single = client.get("/api/v1/ecological/sites/site_yamuna_oza")
    assert r_single.status_code == 200
    assert r_single.json()["site_name"] == "Yamuna Khadar Biodiversity Zone"

    # Single site 404
    r_404 = client.get("/api/v1/ecological/sites/unknown_site_xyz")
    assert r_404.status_code == 404

    # GET scan
    r_scan_get = client.get("/api/v1/ecological/scan?site_id=site_deepor_beel")
    assert r_scan_get.status_code == 200
    data_scan_get = r_scan_get.json()
    assert data_scan_get["site_id"] == "site_deepor_beel"
    assert "eti_score" in data_scan_get

    # POST scan
    payload = {
        "site_id": "site_pallikaranai_marsh",
        "current_ndbi": 0.15,
        "current_ndvi": 0.40,
        "current_mndwi": 0.25,
        "notes": "Citizen drone report of illegal construction debris dumping"
    }
    r_scan_post = client.post("/api/v1/ecological/scan", json=payload)
    assert r_scan_post.status_code == 200
    data_scan_post = r_scan_post.json()
    assert data_scan_post["site_id"] == "site_pallikaranai_marsh"
    assert data_scan_post["delta_ndbi"] > 0.0

    # Active threats
    r_threats = client.get("/api/v1/ecological/threats")
    assert r_threats.status_code == 200
    assert isinstance(r_threats.json(), list)

    # Spec
    r_spec = client.get("/api/v1/ecological/spec")
    assert r_spec.status_code == 200
    assert "ecological_threat_index" in r_spec.json()["governing_invariants"]


def test_ecological_mcp_tool_execution():
    """Verify MCP Tool execution for scan_ecological_threats."""
    assert "scan_ecological_threats" in TOOLS_REGISTRY

    params = {
        "site_id": "site_mithi_mangrove",
        "current_ndbi": 0.10,
        "current_ndvi": 0.45,
        "current_mndwi": 0.20,
        "notes": "MCP automated change detection audit"
    }
    result = execute_tool_logic("scan_ecological_threats", params)
    assert result["site_id"] == "site_mithi_mangrove"
    assert "eti_score" in result
    assert "threat_tier" in result
    assert "enforcement_recommendation" in result
