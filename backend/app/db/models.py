"""
AEGIS Persistence Models & Data Store
Conforms to PRD 2: Section 10 Persistence model proposal.
Tracks analysis_runs, evidence_bundles, and anchor_transactions state machine.
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import json
import uuid


class AnalysisRun(BaseModel):
    analysis_id: str = Field(..., description="Unique analysis run identifier")
    created_at_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    location_label: str
    latitude: float
    longitude: float
    data_mode: str = "live"
    output_payload: Dict[str, Any]
    checksum: str


class EvidenceBundleRecord(BaseModel):
    evidence_id: str = Field(..., description="Unique evidence bundle identifier")
    analysis_id: str
    schema_version: str = "1.0.0"
    canonicalization_version: str = "aegis-canonical-json-v1"
    hash_algorithm: str = "keccak256"
    digest: str = Field(..., description="0x-prefixed Keccak-256 content digest")
    bundle_payload: Dict[str, Any]
    created_at_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    anchor_status: str = Field(default="NOT_ANCHORED")  # NOT_ANCHORED, SUBMITTED, PENDING, CONFIRMED, REVERTED
    tx_hash: Optional[str] = None


class AnchorTransactionRecord(BaseModel):
    transaction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    evidence_id: str
    chain_id: int
    registry_address: str
    signer_address: str
    tx_hash: str
    status: str = "SUBMITTED"  # SUBMITTED, PENDING, CONFIRMED, REVERTED
    block_number: Optional[int] = None
    confirmations: int = 0
    submitted_at_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    confirmed_at_utc: Optional[str] = None
    error_code: Optional[str] = None


class InMemoryEvidenceStore:
    """Thread-safe state repository for analysis, evidence bundles, and blockchain transactions."""
    def __init__(self):
        self.analyses: Dict[str, AnalysisRun] = {}
        self.bundles: Dict[str, EvidenceBundleRecord] = {}
        self.transactions: Dict[str, AnchorTransactionRecord] = {}

    def save_analysis(self, record: AnalysisRun) -> None:
        self.analyses[record.analysis_id] = record

    def get_analysis(self, analysis_id: str) -> Optional[AnalysisRun]:
        return self.analyses.get(analysis_id)

    def save_bundle(self, record: EvidenceBundleRecord) -> None:
        self.bundles[record.evidence_id] = record

    def get_bundle(self, evidence_id: str) -> Optional[EvidenceBundleRecord]:
        return self.bundles.get(evidence_id)

    def save_transaction(self, record: AnchorTransactionRecord) -> None:
        self.transactions[record.transaction_id] = record
        # Update corresponding bundle status
        if record.evidence_id in self.bundles:
            bundle = self.bundles[record.evidence_id]
            bundle.anchor_status = record.status
            bundle.tx_hash = record.tx_hash

    def get_transaction(self, transaction_id: str) -> Optional[AnchorTransactionRecord]:
        return self.transactions.get(transaction_id)

    def get_transaction_by_evidence(self, evidence_id: str) -> Optional[AnchorTransactionRecord]:
        for tx in self.transactions.values():
            if tx.evidence_id == evidence_id:
                return tx
        return None

    def clear(self) -> None:
        self.analyses.clear()
        self.bundles.clear()
        self.transactions.clear()


evidence_store = InMemoryEvidenceStore()
