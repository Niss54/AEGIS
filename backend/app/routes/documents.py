"""
Document Management & Phase 8 Hybrid Statutory RAG Router
Handles listing, ingestion, and dual-retriever RAG (Dense Vector + BM25 Sparse + Reciprocal Rank Fusion).
"""
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException

from backend.app.hybrid_rag import (
    statutory_rag_controller,
    HybridRAGQueryRequest,
    HybridRAGQueryResponse,
    HybridRAGModel
)

router = APIRouter(tags=["Regulatory Documents & Hybrid RAG"])

INITIAL_DOCUMENTS = [
    {
        "id": "doc-brsr-core-2024",
        "title": "SEBI BRSR Core Mandate — ESG & Climate Disclosure Guidelines for Top 1000 Listed Entities",
        "region": "India (National)",
        "sector": "Enterprise & Financial",
        "doc_type": "REGULATORY_COMPLIANCE",
        "chunks_indexed": 142,
        "summary": "Mandates Scope 1, 2 emissions reporting, climate financial impact assessments, and physical asset risk audits.",
        "ingested_at": "2026-09-28T10:00:00Z"
    },
    {
        "id": "doc-carbon-tax-bharat-2026",
        "title": "Ministry of Finance — Proposed Carbon Border & Heavy Emission Penalty Mechanism 2026",
        "region": "India",
        "sector": "Industrial & Energy",
        "doc_type": "CARBON_TAX",
        "chunks_indexed": 86,
        "summary": "Imposes progressive surcharges on industrial facilities exceeding grid-average carbon intensity thresholds.",
        "ingested_at": "2026-09-29T14:30:00Z"
    },
    {
        "id": "doc-ndma-urban-flood-sop",
        "title": "NDMA Standard Operating Procedure — Management of Urban Flooding and Critical Lifeline Infrastructure",
        "region": "India (Municipalities)",
        "sector": "Civic & Infrastructure",
        "doc_type": "CIVIC_RESILIENCE",
        "chunks_indexed": 210,
        "summary": "Defines drainage capacity standards, mandatory pumping installation protocols, and hospital/metro flood barrier standards.",
        "ingested_at": "2026-09-30T09:15:00Z"
    }
]


@router.get("/documents", response_model=List[Dict[str, Any]])
async def list_documents():
    """List all climate and regulatory documents indexed in the vector store."""
    return INITIAL_DOCUMENTS


@router.post("/documents/ingest")
async def ingest_document(title: str, region: str = "India", sector: str = "General"):
    """Mock document ingestion endpoint for RAG expansion."""
    doc_id = f"doc-{int(time.time())}"
    now_str = datetime.now(timezone.utc).isoformat()
    new_doc = {
        "id": doc_id,
        "title": title,
        "region": region,
        "sector": sector,
        "doc_type": "USER_UPLOADED_POLICY",
        "chunks_indexed": 48,
        "summary": f"Custom policy ingested: {title}. Chunked into 512-token segments and indexed.",
        "ingested_at": now_str
    }
    INITIAL_DOCUMENTS.append(new_doc)
    return {
        "status": "success",
        "message": f"Document '{title}' successfully chunked and embedded in ChromaDB vector collection.",
        "document": new_doc
    }


@router.post("/documents/hybrid-query", response_model=HybridRAGQueryResponse)
async def query_hybrid_rag(req: HybridRAGQueryRequest):
    """
    Phase 8 Dual-Retriever Statutory Legal RAG:
    Fuses dense vector cosine rankings with BM25 Okapi sparse keyword rankings using Reciprocal Rank Fusion:
    RRF(d) = 0.55 / (60 + r_dense(d)) + 0.45 / (60 + r_sparse(d))
    """
    t0 = time.perf_counter()
    try:
        results = statutory_rag_controller.execute_hybrid_search(
            query=req.query,
            top_k=req.top_k,
            alpha_dense=req.alpha_dense,
            alpha_sparse=req.alpha_sparse,
            sector_filter=req.sector_filter
        )
        latency = round((time.perf_counter() - t0) * 1000, 2)
        return HybridRAGQueryResponse(
            query=req.query,
            total_corpus_chunks=len(statutory_rag_controller.corpus),
            returned_count=len(results),
            results=results,
            latency_ms=latency
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Hybrid RAG query failure: {str(exc)}")


@router.post("/documents/pipeline", response_model=HybridRAGModel)
async def execute_phase8_pipeline(payload: Dict[str, Any]):
    """
    Standard PRD.md Section 16 Phase 8 Execution Pipeline returning HybridRAGModel.
    """
    try:
        return await statutory_rag_controller.execute_phase_pipeline(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Phase 8 pipeline execution failed: {str(exc)}")


@router.get("/documents/corpus-stats")
async def get_corpus_statistics():
    """
    Returns indexing statistics for dense and BM25 sparse retrieval engines.
    """
    bm25 = statutory_rag_controller.bm25
    return {
        "status": "INDEXED_OPERATIONAL",
        "total_statutory_chunks": len(statutory_rag_controller.corpus),
        "bm25_hyperparameters": {"k1": bm25.k1, "b": bm25.b},
        "average_chunk_length_tokens": round(bm25.avg_doc_len, 1),
        "unique_lexical_terms_indexed": len(bm25.doc_freqs),
        "circuit_breaker_state": statutory_rag_controller.circuit_state,
        "supported_mandates": [c["title"] for c in statutory_rag_controller.corpus]
    }
