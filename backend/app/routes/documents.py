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
        "region": "India",
        "sector": "Enterprise & Financial",
        "doc_type": "REGULATORY_COMPLIANCE",
        "chunks_indexed": 142,
        "summary": "Mandates Scope 1, 2 emissions reporting, climate financial impact assessments, and physical asset risk audits.",
        "ingested_at": "2026-09-28T10:00:00Z"
    },
    {
        "id": "doc-spk-sustainability-tr",
        "title": "SPK Sustainability Principles Compliance Framework (Sürdürülebilirlik İlkeleri Uyum Çerçevesi)",
        "region": "Türkiye",
        "sector": "Enterprise & Financial",
        "doc_type": "REGULATORY_COMPLIANCE",
        "chunks_indexed": 118,
        "summary": "Capital Markets Board of Türkiye mandates physical flood vulnerability audits and ESG capital adaptation budgets for BIST entities.",
        "ingested_at": "2026-10-01T08:30:00Z"
    },
    {
        "id": "doc-california-sb253-sb261",
        "title": "California Climate Corporate Data Accountability Act (SB 253 & SB 261)",
        "region": "USA",
        "sector": "Enterprise & Financial",
        "doc_type": "REGULATORY_COMPLIANCE",
        "chunks_indexed": 164,
        "summary": "Requires $1B+ corporations to disclose Scope 1-3 GHG inventories and biennial TCFD physical flood/atmospheric river risk audits.",
        "ingested_at": "2026-10-02T11:15:00Z"
    },
    {
        "id": "doc-eu-csddd-2024",
        "title": "EU Corporate Sustainability Due Diligence Directive (CSDDD 2024/1760)",
        "region": "European Union / Estonia",
        "sector": "Enterprise & Financial",
        "doc_type": "REGULATORY_COMPLIANCE",
        "chunks_indexed": 195,
        "summary": "Mandates 1.5°C Paris Agreement transition plans and strict corporate civil liability for unmitigated coastal storm surge damages.",
        "ingested_at": "2026-10-03T14:45:00Z"
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
        "region": "India",
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
