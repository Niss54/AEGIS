"""
AEGIS-CLIMATE — Phase 2: Enterprise Hybrid RAG & Redis Vector Cache Test Suite
Validates:
1. Multi-jurisdiction regulatory corpus ingestion (India, Türkiye, USA, Estonia/EU)
2. Geolocation/jurisdiction-aware routing (SPK, California SB 253, EU CSDDD, SEBI BRSR)
3. Sub-10ms L1/Redis hybrid cache retrieval
4. AquaFHIR Critical Infrastructure Vector calculation in Agent 2
5. REST API integration & cache telemetry
"""
import time
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.rag.corpus import GLOBAL_REGULATORY_CORPUS
from backend.app.rag.hybrid_cache import HybridRegulatoryCache, hybrid_cache
from backend.app.rag.engine import HybridRegulatoryRAGEngine, normalize_jurisdiction_target
from backend.app.agent2_geo import chronic_geo_engine
from backend.app.schemas import CriticalInfrastructureVector

client = TestClient(app)


def test_multi_jurisdiction_corpus_integrity():
    """Verify that regulatory corpus contains required national and regional frameworks."""
    assert len(GLOBAL_REGULATORY_CORPUS) >= 9

    regions = {doc["region"] for doc in GLOBAL_REGULATORY_CORPUS}
    assert "India" in regions
    assert "Turkey" in regions
    assert "USA" in regions
    assert "Estonia" in regions or "European Union" in regions

    ids = [doc["id"] for doc in GLOBAL_REGULATORY_CORPUS]
    assert "sebi-brsr-principle6" in ids
    assert "spk-sustainability-principles-tr" in ids
    assert "california-sb253-climate-act" in ids
    assert "eu-csddd-corporate-due-diligence" in ids

    for doc in GLOBAL_REGULATORY_CORPUS:
        assert doc["id"]
        assert doc["title"]
        assert doc["text"]
        assert doc["country_iso"] in ["IN", "TR", "US", "EE", "EU", "GLOBAL"]


def test_jurisdiction_normalization():
    """Verify normalization heuristic maps city/state names to target jurisdictions."""
    assert normalize_jurisdiction_target("Istanbul Marmara Basin") == "Turkey"
    assert normalize_jurisdiction_target("Kastamonu Bozkurt") == "Turkey"
    assert normalize_jurisdiction_target("Orange County Santa Ana River") == "USA"
    assert normalize_jurisdiction_target("Pärnu Bay Coastal Strip") == "Estonia"
    assert normalize_jurisdiction_target("Lucknow Gomti Basin") == "India"
    assert normalize_jurisdiction_target("Mumbai Industrial Zone") == "India"


def test_turkish_spk_retrieval_routing():
    """Verify Turkish SPK and AFAD regulations are retrieved when querying for Istanbul/Turkey."""
    engine = HybridRegulatoryRAGEngine()
    results = engine.query(
        query_text="corporate ESG disclosure and flood risk stress testing",
        region="Turkey",
        sector="Enterprise & Financial",
        top_k=2
    )
    assert len(results) >= 1
    top_doc = results[0]
    # Either SPK or Turkish disaster law should be top
    doc_id = top_doc["id"]
    assert doc_id in ["spk-sustainability-principles-tr", "tr-climate-disaster-law-7269"]
    assert top_doc["metadata"]["region"] == "Turkey"


def test_california_sb253_retrieval_routing():
    """Verify California SB 253 / SB 261 regulations are retrieved when querying for Orange County / USA."""
    engine = HybridRegulatoryRAGEngine()
    results = engine.query(
        query_text="Scope 3 emissions and physical flood risk disclosure mandate",
        region="USA",
        sector="Enterprise & Financial",
        top_k=2
    )
    assert len(results) >= 1
    top_doc = results[0]
    assert top_doc["id"] in ["california-sb253-climate-act", "california-sb261-financial-risk"]
    assert top_doc["metadata"]["region"] == "USA"


def test_estonia_csddd_retrieval_routing():
    """Verify EU CSDDD and EU Taxonomy regulations are retrieved when querying for Estonia / EU."""
    engine = HybridRegulatoryRAGEngine()
    results = engine.query(
        query_text="coastal storm surge flood risk corporate due diligence transition plan",
        region="Estonia",
        sector="Enterprise & Financial",
        top_k=2
    )
    assert len(results) >= 1
    top_doc = results[0]
    assert top_doc["id"] in ["eu-csddd-corporate-due-diligence", "eu-taxonomy-climate-adaptation"]
    assert top_doc["metadata"]["region"] in ["Estonia", "European Union"]


def test_india_sebi_brsr_retrieval_routing():
    """Verify SEBI BRSR and NDMA regulations are retrieved when querying for India / Lucknow."""
    engine = HybridRegulatoryRAGEngine()
    results = engine.query(
        query_text="BRSR core physical flood damage disclosure and penalties",
        region="India",
        sector="Enterprise & Financial",
        top_k=2
    )
    assert len(results) >= 1
    top_doc = results[0]
    assert top_doc["id"] in ["sebi-brsr-principle6", "mof-carbon-tax-2026", "ndma-urban-flood-sop-sec14"]
    assert top_doc["metadata"]["region"] == "India"


def test_hybrid_cache_sub_10ms_latency():
    """Verify that cached regulatory retrieval executes in strictly sub-10ms (sub-5ms typical)."""
    test_cache = HybridRegulatoryCache()
    engine = HybridRegulatoryRAGEngine(cache=test_cache)

    q = "benchmark physical asset transition risk and resilience standards"
    # First call: Cache MISS
    t_miss_0 = time.perf_counter()
    res_miss = engine.query(query_text=q, region="USA", top_k=2)
    t_miss_ms = (time.perf_counter() - t_miss_0) * 1000.0

    # Second call: Cache HIT
    t_hit_0 = time.perf_counter()
    res_hit = engine.query(query_text=q, region="USA", top_k=2)
    t_hit_ms = (time.perf_counter() - t_hit_0) * 1000.0

    assert len(res_hit) == len(res_miss)
    assert res_hit[0]["cached"] is True
    # Strict sub-10ms requirement from PRD
    assert t_hit_ms < 10.0, f"Cache hit took {t_hit_ms:.2f}ms, expected < 10ms"

    # Verify telemetry stats
    stats = test_cache.get_stats()
    assert stats["total_queries"] >= 2
    assert stats["cache_hits"] >= 1
    assert stats["l1_hits"] >= 1
    assert stats["hit_rate_pct"] > 0.0


def test_aquafir_critical_infrastructure_vector_calculation():
    """Verify AquaFHIR Critical Infrastructure Vector calculations under different flood severities."""
    # Scenario A: Severe flood (depth ~ 100cm, overflow > 80%)
    res_severe = chronic_geo_engine.analyze_structural_exposure(
        lat=41.0082,
        lon=28.9784,
        risk_score=0.85,
        precipitation_24h_mm=130.0,
        soil_saturation_pct=90.0,
        elevation_m=12.0
    )
    assert "critical_infrastructure_vector" in res_severe
    civ_severe = res_severe["critical_infrastructure_vector"]
    assert civ_severe["power_substations_at_risk"] >= 1
    assert civ_severe["healthcare_facilities_exposed"] >= 1
    assert civ_severe["evacuation_corridors_submerged"] >= 1
    assert civ_severe["drainage_conduits_overcapacity_pct"] > 70.0

    # Validate against Pydantic schema
    civ_model = CriticalInfrastructureVector(**civ_severe)
    assert civ_model.power_substations_at_risk >= 1

    # Scenario B: Minor waterlogging (low depth, small precipitation)
    res_minor = chronic_geo_engine.analyze_structural_exposure(
        lat=26.8467,
        lon=80.9462,
        risk_score=0.35,
        precipitation_24h_mm=15.0,
        soil_saturation_pct=40.0,
        elevation_m=123.0
    )
    civ_minor = res_minor["critical_infrastructure_vector"]
    assert civ_minor["healthcare_facilities_exposed"] == 0
    assert civ_minor["drainage_conduits_overcapacity_pct"] < civ_severe["drainage_conduits_overcapacity_pct"]


def test_policy_rag_endpoint_with_cache_stats():
    """Verify /api/v1/tools/policy-rag returns region-filtered results and cache telemetry."""
    # Query for Turkish SPK regulations via REST API
    res = client.post("/api/v1/tools/policy-rag?query=SPK%20climate%20reporting&region=Turkey&top_k=2")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["results_count"] >= 1
    assert "cache_stats" in data
    assert "total_queries" in data["cache_stats"]
    assert any("SPK" in c["metadata"].get("title", "") for c in data["clauses"])


def test_analyze_pipeline_critical_infra_and_rag():
    """Verify full end-to-end analyze pipeline generates critical infrastructure and regional RAG."""
    payload = {
        "lat": 41.0082,
        "lon": 28.9784,
        "location_name": "Istanbul Marmara Industrial Port",
        "simulated_additional_rain_mm": 110.0,
        "simulated_saturation_pct_override": 92.0
    }
    res = client.post("/api/v1/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["agent1"]["risk_score"] > 0.65
    assert data["agent2"] is not None
    assert data["agent2"]["critical_infrastructure_vector"] is not None
    civ = data["agent2"]["critical_infrastructure_vector"]
    assert civ["power_substations_at_risk"] >= 1

    # If Agent 3 triggered, check applicable regulations
    if data["agent3"]:
        regs = data["agent3"]["applicable_regulations"]
        assert len(regs) >= 1
        # Should contain Turkish SPK / AFAD regulations
        assert any("SPK" in r or "Disaster" in r or "Climate" in r for r in regs)
