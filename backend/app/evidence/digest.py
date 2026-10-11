"""
Ethereum Keccak-256 Cryptographic Digest Engine
Conforms to PRD 2: Section 6, E-066, E-067, E-068.
Strictly uses Ethereum Keccak-256 (NOT FIPS SHA3-256).
"""
import logging
from typing import Dict, Any, Tuple
from backend.app.evidence.schema import ClimateEvidenceBundle
from backend.app.evidence.canonicalize import canonicalize_bundle, canonicalize_dict

logger = logging.getLogger("aegis.digest")


def keccak256_hex(data: bytes) -> str:
    """
    Computes genuine Ethereum Keccak-256 digest over bytes.
    Returns 0x-prefixed 64-character hexadecimal string.
    """
    try:
        from Crypto.Hash import keccak
        k = keccak.new(digest_bits=256)
        k.update(data)
        return "0x" + k.hexdigest()
    except ImportError:
        # Fallback to web3 / eth_hash implementation
        from web3 import Web3
        digest_bytes = Web3.keccak(data)
        return "0x" + digest_bytes.hex().replace("0x", "")


def compute_bundle_digest(bundle: ClimateEvidenceBundle) -> str:
    """
    Computes deterministic Keccak-256 digest over the canonicalized bundle preimage.
    PRD 2: E-067 Deterministic server-side digest calculation.
    """
    canonical_bytes = canonicalize_bundle(bundle)
    return keccak256_hex(canonical_bytes)


def verify_bundle_digest(bundle_dict: Dict[str, Any], expected_digest: str) -> Tuple[bool, str]:
    """
    Recomputes the canonical Keccak-256 digest from raw bundle dictionary
    and checks against the expected digest string.
    Returns (matches: bool, computed_digest: str).
    """
    canonical_bytes = canonicalize_dict(bundle_dict)
    computed = keccak256_hex(canonical_bytes)
    matches = computed.lower() == expected_digest.lower()
    return matches, computed
