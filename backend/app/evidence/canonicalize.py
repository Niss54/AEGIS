"""
Deterministic Evidence Canonicalizer
Conforms to PRD 2: Section 6 Canonicalization Requirements (E-062 through E-065).
Produces byte-identical JSON across Python and TypeScript implementations.
"""
import json
import math
import unicodedata
from typing import Any, Dict
from backend.app.evidence.schema import ClimateEvidenceBundle


MUTABLE_TRANSPORT_FIELDS = {
    "digest",
    "content_digest",
    "transaction_hash",
    "tx_hash",
    "anchor_status",
    "chain_id",
    "block_number",
    "receipt",
    "verifier_result",
    "confirmations"
}


def _normalize_obj(obj: Any) -> Any:
    """Recursively normalizes data structures for deterministic serialization."""
    if isinstance(obj, dict):
        # Alphabetically sort keys, excluding mutable transport metadata
        return {
            k: _normalize_obj(v)
            for k, v in sorted(obj.items())
            if k not in MUTABLE_TRANSPORT_FIELDS
        }
    elif isinstance(obj, list):
        return [_normalize_obj(item) for item in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            raise ValueError("Cannot canonicalize NaN or Infinity float values.")
        # Round to 6 decimal places to eliminate platform-dependent float rounding discrepancies
        rounded = round(obj, 6)
        if rounded.is_integer():
            return int(rounded)
        return rounded
    elif isinstance(obj, str):
        # Unicode Normalization Form C (NFC)
        return unicodedata.normalize("NFC", obj)
    return obj


def canonicalize_bundle(bundle: ClimateEvidenceBundle) -> bytes:
    """
    Serializes a validated ClimateEvidenceBundle into canonical UTF-8 bytes.
    Guarantees:
    - Keys sorted alphabetically
    - No formatting whitespace (separators=(',', ':'))
    - Unicode NFC normalization
    - Mutable transport metadata stripped from preimage
    """
    raw_dict = bundle.model_dump(exclude_none=False)
    normalized = _normalize_obj(raw_dict)
    canonical_str = json.dumps(
        normalized,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":")
    )
    return canonical_str.encode("utf-8")


def canonicalize_dict(data: Dict[str, Any]) -> bytes:
    """Canonicalizes an arbitrary dictionary conforming to the evidence schema."""
    normalized = _normalize_obj(data)
    canonical_str = json.dumps(
        normalized,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":")
    )
    return canonical_str.encode("utf-8")
