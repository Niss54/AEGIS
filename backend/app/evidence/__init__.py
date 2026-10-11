"""
AEGIS Climate Evidence Module
Conforms to PRD 2: Section 6 Normative Evidence Definition.
"""
from backend.app.evidence.schema import (
    ClimateEvidenceBundle,
    AnalysisSection,
    EvidenceLocation,
    AnalysisInputItem,
    TransformationItem,
    RiskOutputSection,
    ExposureOutputSection,
    PolicyOutputSection,
    ModelManifestSection
)
from backend.app.evidence.canonicalize import canonicalize_bundle
from backend.app.evidence.digest import compute_bundle_digest, verify_bundle_digest

__all__ = [
    "ClimateEvidenceBundle",
    "AnalysisSection",
    "EvidenceLocation",
    "AnalysisInputItem",
    "TransformationItem",
    "RiskOutputSection",
    "ExposureOutputSection",
    "PolicyOutputSection",
    "ModelManifestSection",
    "canonicalize_bundle",
    "compute_bundle_digest",
    "verify_bundle_digest"
]
