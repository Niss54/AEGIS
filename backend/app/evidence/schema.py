"""
Pydantic Data Models for Climate Evidence Bundle
Conforms to PRD 2: Section 6 Normative Definition and E-061.
Validates inputs, ranges, timestamps, and enforces additionalProperties=False.
"""
from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict
import math


class EvidenceLocation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    region_label: str = Field(..., description="Human-readable geographic label")
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    coordinate_commitment: Optional[str] = Field(default=None, description="Optional blinded hash for privacy")


class AnalysisInputItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str = Field(..., description="Primary observation provider")
    variable: str = Field(..., description="Environmental parameter name")
    value: float = Field(..., description="Observed numeric value")
    unit: str = Field(..., description="Physical measurement unit")
    is_synthetic: bool = Field(default=False)
    timestamp_utc: Optional[str] = Field(default=None)

    @field_validator("value")
    @classmethod
    def validate_finite_number(cls, v: float) -> float:
        if math.isnan(v) or math.isinf(v):
            raise ValueError("Numeric inputs must be finite numbers; NaN and Infinity are forbidden.")
        return v


class TransformationItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step: str
    method: str
    description: str


class RiskOutputSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_tier: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    dominant_factor: str
    probabilities: Optional[Dict[str, float]] = None


class ExposureOutputSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    exposure_tier: str
    waterlogging_depth_cm: int = Field(..., ge=0)
    buildings_at_risk: int = Field(..., ge=0)
    drainage_overflow_pct: float = Field(..., ge=0.0, le=100.0)
    damage_estimate_inr: Optional[float] = Field(default=None, ge=0.0)
    methodology: str = Field(default="topographical_heuristic_hazus")


class PolicyOutputSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    var_estimate_inr: float = Field(..., ge=0.0)
    stranded_asset_risk: Literal["LOW", "MEDIUM", "HIGH"]
    compliance_gap_pct: int = Field(..., ge=0, le=100)
    applicable_regulations: List[str] = Field(default_factory=list)
    legal_disclaimer: str = Field(default="This analysis is for research and risk-awareness purposes only.")


class AnalysisSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    analysis_id: str = Field(..., min_length=1)
    location: EvidenceLocation
    created_at_utc: str = Field(..., description="ISO-8601 UTC with trailing Z")
    data_mode: Literal["live", "fixture", "synthetic"]
    inputs: List[AnalysisInputItem]
    transformations: List[TransformationItem] = Field(default_factory=list)
    risk_output: RiskOutputSection
    exposure_output: ExposureOutputSection
    policy_output: PolicyOutputSection

    @field_validator("created_at_utc")
    @classmethod
    def validate_utc_timestamp(cls, v: str) -> str:
        if not v.endswith("Z"):
            raise ValueError("Timestamp must be UTC ISO-8601 ending with 'Z'")
        return v


class ModelManifestSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model_id: str
    artifact_sha256: str
    feature_schema_version: str
    algorithm: Optional[str] = None
    features: Optional[List[str]] = None


class ClimateEvidenceBundle(BaseModel):
    """
    Top-level Normative Climate Evidence Bundle.
    Conforms to PRD 2: Section 6.
    """
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0.0"] = "1.0.0"
    evidence_id: str = Field(..., min_length=1)
    analysis: AnalysisSection
    model_manifest: ModelManifestSection
    code_revision: str
    limitations: List[str] = Field(default_factory=list)
    hash_algorithm: Literal["keccak256"] = "keccak256"
    canonicalization_version: Literal["aegis-canonical-json-v1"] = "aegis-canonical-json-v1"
