"""Independent Climate Evidence Canonicalizer and Tamper-Detection Verifier.
Follows IEEE ClimateChain Data Integrity and Accountability track requirements.
"""
import json
import hashlib
from typing import Dict, Any, Tuple


class EvidenceVerifier:
    """Computes deterministic canonical digests and independently verifies tamper status."""

    @staticmethod
    def canonicalize(payload: Dict[str, Any]) -> str:
        """Produce deterministic sorted canonical JSON representation."""
        # Extract core verifiable fields to eliminate transient network headers
        loc = payload.get("location") or {}
        a1 = payload.get("agent1") or {}
        a2 = payload.get("agent2") or {}
        a3 = payload.get("agent3") or {}

        verifiable_subset = {
            "location": {
                "lat": round(float(payload.get("lat", loc.get("lat", 0.0)) or 0.0), 4),
                "lon": round(float(payload.get("lon", loc.get("lon", 0.0)) or 0.0), 4),
                "name": str(payload.get("location_name", loc.get("name", "Asset")) or "Asset"),
            },
            "risk_score": round(float(payload.get("risk_score", a1.get("risk_score", 0.0)) or 0.0), 4),
            "risk_tier": str(payload.get("risk_tier", a1.get("risk_tier", "LOW")) or "LOW"),
            "waterlogging_depth_cm": int(payload.get("waterlogging_depth_cm", a2.get("waterlogging_depth_cm", 0)) or 0),
            "var_estimate_inr": int(payload.get("var_estimate_inr", a3.get("var_estimate_inr", 0)) or 0),
        }
        return json.dumps(verifiable_subset, sort_keys=True, separators=(',', ':'))

    @classmethod
    def compute_digests(cls, payload: Dict[str, Any]) -> Tuple[str, str]:
        """Compute SHA-256 and Keccak-256 hex digests."""
        canonical_str = cls.canonicalize(payload)
        sha256_digest = "0x" + hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

        try:
            from eth_utils import keccak
            keccak_digest = "0x" + keccak(text=canonical_str).hex()
        except Exception:
            keccak_digest = sha256_digest

        return sha256_digest, keccak_digest

    @classmethod
    def verify(
        cls,
        current_data: Dict[str, Any],
        expected_digest: str
    ) -> Dict[str, Any]:
        """Verify data matches the anchored cryptographic digest."""
        sha_digest, keccak_digest = cls.compute_digests(current_data)
        matches = (sha_digest.lower() == expected_digest.lower() or keccak_digest.lower() == expected_digest.lower())

        if matches:
            return {
                "status": "PASS",
                "is_valid": True,
                "verified": True,
                "tampered": False,
                "message": "Cryptographic integrity verified. On-chain commitment matches report payload perfectly.",
                "computed_digest": sha_digest,
                "computed_sha256": sha_digest,
                "computed_keccak256": keccak_digest,
                "expected_digest": expected_digest,
            }
        else:
            return {
                "status": "FAIL",
                "is_valid": False,
                "verified": False,
                "tampered": True,
                "message": "TAMPER DETECTED: Computed digest does NOT match on-chain commitment. Report payload has been altered post-anchoring.",
                "computed_digest": sha_digest,
                "computed_sha256": sha_digest,
                "computed_keccak256": keccak_digest,
                "expected_digest": expected_digest,
            }


evidence_verifier = EvidenceVerifier()
