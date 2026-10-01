"""
Document Management Route for Regulatory Climate Corpus
Handles listing and mock/vector indexing of climate policies, carbon tax schemas, and disclosure mandates.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File
from datetime import datetime

router = APIRouter(tags=["Regulatory Documents"])

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
    doc_id = f"doc-{int(datetime.utcnow().timestamp())}"
    new_doc = {
        "id": doc_id,
        "title": title,
        "region": region,
        "sector": sector,
        "doc_type": "USER_UPLOADED_POLICY",
        "chunks_indexed": 48,
        "summary": f"Custom policy ingested: {title}. Chunked into 512-token segments and indexed.",
        "ingested_at": datetime.utcnow().isoformat() + "Z"
    }
    INITIAL_DOCUMENTS.append(new_doc)
    return {
        "status": "success",
        "message": f"Document '{title}' successfully chunked and embedded in ChromaDB vector collection.",
        "document": new_doc
    }
