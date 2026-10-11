"""
Tests for Evidence Canonicalization, Digest Computation & Tamper Detection
Conforms to PRD 2: Section 6, 11 (P0 gates) and E-061 through E-072.
"""
import json
import pytest
import hashlib
from pathlib import Path

from backend.app.evidence.schema import ClimateEvidenceBundle
from backend.app.evidence.canonicalize import canonicalize_bundle, canonicalize_dict
from backend.app.evidence.digest import compute_bundle_digest, verify_bundle_digest, keccak256_hex
from backend.app.evidence.service import evidence_service


@pytest.fixture
def golden_bundle_dict():
    fixture_path = Path(__file__).parent / "fixtures" / "golden_evidence_bundle.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def golden_bundle(golden_bundle_dict):
    return ClimateEvidenceBundle.model_validate(golden_bundle_dict)


def test_schema_validation_valid_bundle(golden_bundle):
    """PRD 2: E-061 Valid bundle complies with ClimateEvidenceBundle schema."""
    assert golden_bundle.schema_version == "1.0.0"
    assert golden_bundle.evidence_id == "ev_golden_fixture_001"
    assert golden_bundle.analysis.risk_output.risk_tier == "CRITICAL"
    assert golden_bundle.analysis.created_at_utc.endswith("Z")


def test_schema_validation_rejects_missing_required(golden_bundle_dict):
    """PRD 2: E-061 Missing required top-level property is rejected."""
    tampered = golden_bundle_dict.copy()
    del tampered["model_manifest"]
    with pytest.raises(Exception):
        ClimateEvidenceBundle.model_validate(tampered)


def test_schema_validation_rejects_extra_fields(golden_bundle_dict):
    """PRD 2: E-061 Extra unauthorized fields rejected by additionalProperties=False."""
    tampered = golden_bundle_dict.copy()
    tampered["unauthorized_injected_field"] = "malicious_payload"
    with pytest.raises(Exception):
        ClimateEvidenceBundle.model_validate(tampered)


def test_canonicalize_is_deterministic(golden_bundle):
    """PRD 2: E-062 Repeated canonicalization yields identical bytes."""
    bytes1 = canonicalize_bundle(golden_bundle)
    bytes2 = canonicalize_bundle(golden_bundle)
    assert bytes1 == bytes2
    assert isinstance(bytes1, bytes)
    # Check that keys are sorted in the resulting JSON
    decoded = json.loads(bytes1.decode("utf-8"))
    top_keys = list(decoded.keys())
    assert top_keys == sorted(top_keys)


def test_canonicalize_strips_mutable_transport_fields(golden_bundle_dict):
    """PRD 2: Section 6 Mutable metadata (digest, tx_hash, anchor_status) excluded from preimage."""
    raw_with_metadata = golden_bundle_dict.copy()
    raw_with_metadata["digest"] = "0x1234567890abcdef"
    raw_with_metadata["transaction_hash"] = "0x9876543210fedcba"
    raw_with_metadata["anchor_status"] = "CONFIRMED"

    bytes_clean = canonicalize_dict(golden_bundle_dict)
    bytes_with_meta = canonicalize_dict(raw_with_metadata)

    assert bytes_clean == bytes_with_meta, "Mutable transport fields must not alter preimage bytes"


def test_keccak256_differs_from_sha3_256():
    """PRD 2: E-066 Verifies Ethereum Keccak-256 differs from FIPS SHA3-256."""
    test_data = b"AEGIS-CLIMATE-EVIDENCE-TEST"
    eth_keccak = keccak256_hex(test_data).lower()
    fips_sha3 = "0x" + hashlib.sha3_256(test_data).hexdigest().lower()
    assert eth_keccak != fips_sha3, "Ethereum Keccak-256 and FIPS SHA3-256 must not be conflated"


def test_golden_fixture_digest_reproducibility(golden_bundle):
    """Asserts deterministic Keccak-256 digest computation."""
    digest1 = compute_bundle_digest(golden_bundle)
    digest2 = compute_bundle_digest(golden_bundle)
    assert digest1 == digest2
    assert digest1.startswith("0x")
    assert len(digest1) == 66  # "0x" + 64 hex characters


def test_tamper_detection_mutation_fails_and_restoring_passes(golden_bundle_dict):
    """
    PRD 2: P0 Acceptance Gate:
    Original passes -> Single-field mutation fails -> Restoring original passes again.
    """
    # 1. Original passes
    golden_bundle = ClimateEvidenceBundle.model_validate(golden_bundle_dict)
    valid_digest = compute_bundle_digest(golden_bundle)

    res_initial = evidence_service.verify_bundle(golden_bundle_dict, valid_digest)
    assert res_initial["status"] == "PASS"
    assert res_initial["tamper_detected"] is False

    # 2. Mutate 1 field (waterlogging_depth_cm: 85 -> 15)
    tampered_dict = json.loads(json.dumps(golden_bundle_dict))
    tampered_dict["analysis"]["exposure_output"]["waterlogging_depth_cm"] = 15

    res_tampered = evidence_service.verify_bundle(tampered_dict, valid_digest)
    assert res_tampered["status"] == "FAIL"
    assert res_tampered["tamper_detected"] is True
    assert res_tampered["content_digest_matches"] is False
    assert res_tampered["computed_digest"] != valid_digest

    # 3. Restore original -> passes again
    res_restored = evidence_service.verify_bundle(golden_bundle_dict, valid_digest)
    assert res_restored["status"] == "PASS"
    assert res_restored["tamper_detected"] is False
