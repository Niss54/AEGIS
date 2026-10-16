"""
AEGIS Climate Evidence REST API
Conforms to PRD 2: Section 9 API contract proposal and E-097 -> E-099.
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from backend.app.evidence.service import evidence_service
from backend.app.evidence.schema import ClimateEvidenceBundle
from backend.app.db.models import evidence_store
from backend.app.blockchain.chain_client import chain_client
from backend.app.errors import NotFoundError, ValidationError

router = APIRouter(prefix="/evidence", tags=["Evidence & Cryptographic Integrity"])


class CreateEvidenceRequest(BaseModel):
    analysis_id: str = Field(..., description="Correlated multi-agent analysis ID")
    location_label: str = Field("Mumbai Mithi River Basin")
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    weather_vector: Dict[str, Any]
    agent1_result: Dict[str, Any]
    agent2_result: Optional[Dict[str, Any]] = None
    agent3_result: Optional[Dict[str, Any]] = None
    data_mode: str = Field(default="live", description="live, fixture, or synthetic")


class VerifyEvidenceRequest(BaseModel):
    expected_digest: str = Field(..., description="0x-prefixed expected Keccak-256 digest")
    bundle: Dict[str, Any] = Field(..., description="Evidence bundle payload to verify")


@router.post("", summary="Create Canonical Evidence Bundle", response_model=Dict[str, Any])
async def create_evidence_bundle(req: CreateEvidenceRequest):
    """
    Creates, canonicalizes, and computes the Keccak-256 digest for an evidence bundle.
    PRD 2: E-097 Evidence creation endpoint.
    """
    bundle, digest = evidence_service.create_bundle(
        analysis_id=req.analysis_id,
        location_label=req.location_label,
        latitude=req.latitude,
        longitude=req.longitude,
        weather_vector=req.weather_vector,
        agent1_result=req.agent1_result,
        agent2_result=req.agent2_result,
        agent3_result=req.agent3_result,
        data_mode=req.data_mode
    )

    return {
        "status": "CREATED",
        "evidence_id": bundle.evidence_id,
        "analysis_id": req.analysis_id,
        "schema_version": bundle.schema_version,
        "canonicalization_version": bundle.canonicalization_version,
        "hash_algorithm": bundle.hash_algorithm,
        "digest": digest,
        "data_mode": req.data_mode,
        "created_at_utc": bundle.analysis.created_at_utc,
        "anchor_status": "NOT_ANCHORED",
        "bundle": bundle.model_dump()
    }


@router.get("/{evidence_id}", summary="Get Stored Evidence Bundle")
async def get_evidence_bundle(evidence_id: str):
    """
    Retrieves stored evidence bundle and anchoring lifecycle state.
    PRD 2: E-098 Evidence status.
    """
    record = evidence_store.get_bundle(evidence_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Evidence bundle '{evidence_id}' not found")

    return {
        "evidence_id": record.evidence_id,
        "analysis_id": record.analysis_id,
        "schema_version": record.schema_version,
        "digest": record.digest,
        "anchor_status": record.anchor_status,
        "tx_hash": record.tx_hash,
        "created_at_utc": record.created_at_utc,
        "bundle": record.bundle_payload
    }


@router.post("/verify", summary="Verify Climate Evidence Integrity")
async def verify_evidence(req: VerifyEvidenceRequest):
    """
    Independent cryptographic verification endpoint.
    Recomputes Keccak-256 digest and asserts tamper detection.
    PRD 2: E-099 Verify evidence.
    """
    verification = evidence_service.verify_bundle(req.bundle, req.expected_digest)
    return verification


@router.post("/{evidence_id}/anchor", summary="Anchor Evidence On-Chain")
async def anchor_evidence_bundle(evidence_id: str):
    """
    Submits evidence digest to the on-chain ClimateEvidenceRegistry contract.
    PRD 2: Section 8 & Section 9 (E-085 to E-096, E-100).
    """
    record = evidence_store.get_bundle(evidence_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Evidence bundle '{evidence_id}' not found")

    result = await chain_client.anchor_evidence(
        digest=record.digest,
        report_ref=record.analysis_id,
        schema_version=1,
        evidence_id=evidence_id
    )

    return result


@router.get("/{evidence_id}/anchor-status", summary="Get Evidence Anchoring Status")
async def get_anchor_status(evidence_id: str):
    """
    Returns transaction confirmation status, mined block, and block explorer link.
    PRD 2: Section 9 (E-101).
    """
    record = evidence_store.get_bundle(evidence_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Evidence bundle '{evidence_id}' not found")

    tx_rec = evidence_store.get_transaction_by_evidence(evidence_id)
    if not tx_rec:
        return {
            "evidence_id": evidence_id,
            "digest": record.digest,
            "anchor_status": record.anchor_status,
            "tx_hash": record.tx_hash,
            "confirmations": 0,
            "explorer_url": None
        }

    return {
        "evidence_id": evidence_id,
        "digest": record.digest,
        "anchor_status": tx_rec.status,
        "tx_hash": tx_rec.tx_hash,
        "block_number": tx_rec.block_number,
        "confirmations": tx_rec.confirmations,
        "registry_address": tx_rec.registry_address,
        "explorer_url": f"https://amoy.polygonscan.com/tx/{tx_rec.tx_hash}",
        "confirmed_at_utc": tx_rec.confirmed_at_utc
    }

