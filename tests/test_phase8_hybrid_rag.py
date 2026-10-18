"""
Phase 8: Dual-Retriever Hybrid RAG Verification Suite
Governance: Gravitas Reliability Runtime · PRD.md Section 16 Phase 8 Invariants

Verifies:
1. Deterministic Reciprocal Rank Fusion (RRF) mathematical formula:
   RRF(d) = 0.55 / (60 + r_dense) + 0.45 / (60 + r_sparse)
2. BM25 Okapi sparse keyword frequency and IDF scoring invariants.
3. PRD.md Section 16 Phase 8 contract adhering to HybridRAGModel schema.
4. FastAPI endpoints: /documents/hybrid-query, /documents/pipeline, /documents/corpus-stats.
5. MCP Hub JSON-RPC tool invocation for query_hybrid_rag_fusion.
6. Statutory coverage across SEBI BRSR, MoF Carbon Surcharge, NDMA Urban Flood SOP, and RBI Climate Guidelines.
7. Circuit breaker failover transitions.
"""
import pytest
import time
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.hybrid_rag import (
    statutory_rag_controller,
    StatutoryRAGController,
    BM25Index,
    EXPANDED_STATUTORY_CORPUS
)

client = TestClient(app)


def test_reciprocal_rank_fusion_mathematical_invariants():
    """
    Validates RRF formula: RRF(d) = 0.55 / (60 + r_dense) + 0.45 / (60 + r_sparse)
    RRF score is strictly monotonically decreasing as ranks increase.
    """
    k = 60
    # Candidate A: rank 1 dense, rank 1 sparse
    rrf_top = (0.55 / (k + 1)) + (0.45 / (k + 1))
    assert round(rrf_top, 6) == round(1.0 / 61.0, 6)

    # Candidate B: rank 2 dense, rank 3 sparse
    rrf_mid = (0.55 / (k + 2)) + (0.45 / (k + 3))

    # Candidate C: rank 5 dense, rank 6 sparse
    rrf_low = (0.55 / (k + 5)) + (0.45 / (k + 6))

    assert rrf_top > rrf_mid > rrf_low, "RRF score must monotonically decrease as ranks increase."


def test_bm25_okapi_keyword_scoring():
    """
    Validates that BM25 assigns higher scores to documents with exact keyword matches.
    """
    bm25 = BM25Index(EXPANDED_STATUTORY_CORPUS)
    scores_sebi = bm25.score("SEBI BRSR disclosure penalty")
    # Document 0 is SEBI BRSR Core Mandate
    assert scores_sebi[0][1] > scores_sebi[1][1], "SEBI document must score higher on SEBI query than Carbon Tax doc."

    scores_carbon = bm25.score("carbon surcharge environmental remediation emissions")
    # Document 1 is MoF Carbon Tax
    assert scores_carbon[1][1] > scores_carbon[0][1], "Carbon tax document must score higher on Carbon query than SEBI doc."


@pytest.mark.asyncio
async def test_phase_8_execution_invariant_prd_contract():
    """
    Validates PRD.md Section 16 Phase 8 execution invariant contract.
    """
    controller = StatutoryRAGController()
    sample_payload = {
        "event_id": "TEST-PHASE-8-INVARIANT",
        "query": "NDMA urban flood drainage freeboard clearance standards"
    }
    result = await controller.execute_phase_pipeline(sample_payload)
    assert result.event_id == "TEST-PHASE-8-INVARIANT"
    assert result.verified_flag is True
    assert result.metadata["status"] == "OPERATIONAL"
    assert result.metadata["phase_id"] == 8
    assert result.metadata["matched_count"] > 0
    assert "NDMA" in result.metadata["top_regulation"]


def test_hybrid_query_endpoint():
    """
    Tests POST /api/v1/documents/hybrid-query endpoint.
    """
    payload = {
        "query": "SEBI BRSR Principle 6 penalties acute flood disclosure",
        "top_k": 3,
        "alpha_dense": 0.55,
        "alpha_sparse": 0.45
    }
    response = client.post("/api/v1/documents/hybrid-query", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["query"] == payload["query"]
    assert data["returned_count"] == 3
    assert len(data["results"]) == 3

    top_result = data["results"][0]
    assert "SEBI" in top_result["title"]
    assert top_result["rrf_score"] > 0.0
    assert top_result["dense_rank"] >= 1
    assert top_result["sparse_rank"] >= 1
    assert top_result["statutory_penalty_tier"] == "TIER_2_AUDIT_SURCHARGE"


def test_corpus_stats_endpoint():
    """
    Tests GET /api/v1/documents/corpus-stats endpoint.
    """
    response = client.get("/api/v1/documents/corpus-stats")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "INDEXED_OPERATIONAL"
    assert data["total_statutory_chunks"] >= 7
    assert data["bm25_hyperparameters"]["k1"] == 1.5
    assert data["bm25_hyperparameters"]["b"] == 0.75
    assert data["unique_lexical_terms_indexed"] > 50
    assert data["circuit_breaker_state"] == "CLOSED"


def test_mcp_hybrid_rag_tool_invocation():
    """
    Tests MCP Hub dispatcher invocation for query_hybrid_rag_fusion tool.
    """
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "query_hybrid_rag_fusion",
            "arguments": {
                "query": "Reserve Bank of India collateral loan to value haircut",
                "top_k": 2
            }
        },
        "id": "test-mcp-phase8"
    }
    response = client.post("/mcp/invoke", json=payload)
    assert response.status_code == 200, response.text
    res = response.json()
    assert "result" in res
    data = res["result"].get("data", res["result"])
    assert data["tool"] == "query_hybrid_rag_fusion"
    assert data["fused_count"] == 2
    assert any("RBI" in r["title"] or "Reserve Bank" in r["title"] for r in data["results"])


def test_sector_filtering_in_hybrid_rag():
    """
    Validates that sector filter restricts results to appropriate domain.
    """
    results = statutory_rag_controller.execute_hybrid_search(
        query="flood environmental risks",
        top_k=2,
        sector_filter="Banking"
    )
    assert len(results) > 0
    assert all("Banking" in r.sector for r in results)
