"""AEGIS-CHAIN v2.0 Blockchain Gateway Module."""
from backend.app.blockchain.chain_client import chain_client, AEGISChainClient
from backend.app.blockchain.risk_anchor import risk_anchor_service, RiskAnchorService
from backend.app.blockchain.bond_manager import bond_manager, DisasterBondManager
from backend.app.blockchain.cfmc_manager import cfmc_manager, CFMCManager
from backend.app.blockchain.evidence_verifier import evidence_verifier, EvidenceVerifier

__all__ = [
    "chain_client",
    "AEGISChainClient",
    "risk_anchor_service",
    "RiskAnchorService",
    "bond_manager",
    "DisasterBondManager",
    "cfmc_manager",
    "CFMCManager",
    "evidence_verifier",
    "EvidenceVerifier",
]
