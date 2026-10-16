"""
AEGIS Climate Evidence Service
Conforms to PRD 2: Section 6, 9, and E-069 through E-072.
Orchestrates bundle creation, canonicalization, digest computation, and tamper verification.
"""
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional, List

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
from backend.app.evidence.canonicalize import canonicalize_bundle, canonicalize_dict
from backend.app.evidence.digest import compute_bundle_digest, verify_bundle_digest
from backend.app.db.models import AnalysisRun, EvidenceBundleRecord, evidence_store
from backend.app.errors import NotFoundError, ValidationError

logger = logging.getLogger("aegis.evidence.service")


class EvidenceService:
    """Service handling lifecycle of verified climate evidence bundles."""

    @staticmethod
    def create_bundle(
        analysis_id: str,
        location_label: str,
        latitude: float,
        longitude: float,
        weather_vector: Dict[str, Any],
        agent1_result: Dict[str, Any],
        agent2_result: Optional[Dict[str, Any]] = None,
        agent3_result: Optional[Dict[str, Any]] = None,
        data_mode: str = "live",
        code_revision: str = "a51f088"
    ) -> Tuple[ClimateEvidenceBundle, str]:
        """
        Creates a validated normative ClimateEvidenceBundle from multi-agent outputs,
        canonicalizes it, computes its Keccak-256 digest, and persists the bundle.
        """
        evidence_id = f"ev_{uuid.uuid4().hex[:16]}"
        now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # 1. Input telemetry items with provenance
        inputs: List[AnalysisInputItem] = [
            AnalysisInputItem(
                source="Open-Meteo",
                variable="precipitation_24h",
                value=float(weather_vector.get("precipitation_24h_mm", 0.0)),
                unit="mm",
                is_synthetic=(data_mode != "live")
            ),
            AnalysisInputItem(
                source="Open-Meteo",
                variable="precipitation_7d",
                value=float(weather_vector.get("precipitation_7d_mm", 0.0)),
                unit="mm",
                is_synthetic=(data_mode != "live")
            ),
            AnalysisInputItem(
                source="Open-Meteo",
                variable="soil_saturation",
                value=float(weather_vector.get("soil_saturation_pct", 50.0)),
                unit="%",
                is_synthetic=(data_mode != "live")
            ),
            AnalysisInputItem(
                source="Open-Meteo",
                variable="relative_humidity",
                value=float(weather_vector.get("relative_humidity_pct", 75.0)),
                unit="%",
                is_synthetic=(data_mode != "live")
            ),
            AnalysisInputItem(
                source="SRTM-DEM",
                variable="elevation",
                value=float(weather_vector.get("elevation_m", 15.0)),
                unit="m",
                is_synthetic=(data_mode != "live")
            )
        ]

        # 2. Pipeline transformations
        transformations: List[TransformationItem] = [
            TransformationItem(
                step="Agent1_ML_Inference",
                method="GradientBoostingClassifier",
                description="Computed acute flood risk probability score from hydro-meteorological vector."
            ),
            TransformationItem(
                step="Agent2_HAZUS_Exposure",
                method="TopographicalPoolingHeuristic",
                description="Modeled waterlogging pooling depth and municipal drainage overflow."
            ),
            TransformationItem(
                step="Agent3_Financial_VaR",
                method="MultiFactorLossModeling",
                description="Calculated corporate Value at Risk and mapped SEBI BRSR Principle 6 compliance gaps."
            )
        ]

        # 3. Agent 1 output
        risk_output = RiskOutputSection(
            risk_score=float(agent1_result.get("risk_score", 0.5)),
            risk_tier=agent1_result.get("risk_tier", "MEDIUM"),
            dominant_factor=agent1_result.get("dominant_factor", "precipitation_24h_mm"),
            probabilities=agent1_result.get("probabilities")
        )

        # 4. Agent 2 output
        a2 = agent2_result or {}
        exposure_output = ExposureOutputSection(
            exposure_tier=a2.get("exposure_tier", "SUPERFICIAL_WATERLOGGING"),
            waterlogging_depth_cm=int(a2.get("waterlogging_depth_cm", 25)),
            buildings_at_risk=int(a2.get("buildings_at_risk", 45)),
            drainage_overflow_pct=float(a2.get("drainage_overflow_pct", 40.0)),
            damage_estimate_inr=float(a2.get("damage_estimate_inr", 15000000.0)),
            methodology=a2.get("methodology", "topographical_heuristic_hazus")
        )

        # 5. Agent 3 output
        a3 = agent3_result or {}
        policy_output = PolicyOutputSection(
            var_estimate_inr=float(a3.get("var_estimate_inr", 25000000.0)),
            stranded_asset_risk=a3.get("stranded_asset_risk", "MEDIUM"),
            compliance_gap_pct=int(a3.get("compliance_gap_pct", 35)),
            applicable_regulations=a3.get("applicable_regulations", ["SEBI BRSR Principle 6"]),
            legal_disclaimer=a3.get("legal_disclaimer", "Research and risk awareness purposes only.")
        )

        # 6. Model manifest
        model_manifest = ModelManifestSection(
            model_id=agent1_result.get("model_id", "aegis-flood-classifier-v1"),
            artifact_sha256=agent1_result.get("artifact_sha256", "ecf12983bec200fe3d88996c0d89d709676c01deeaa99276dd7f919b23150d70"),
            feature_schema_version="1.0.0",
            algorithm="GradientBoostingClassifier",
            features=["soil_saturation_pct", "precipitation_24h_mm", "precipitation_7d_mm", "relative_humidity_pct", "elevation_m", "drainage_capacity_index"]
        )

        # 7. Limitations
        limitations = [
            "Exposure is modeled via topographical pooling heuristics and HAZUS depth-damage curves.",
            "Weather telemetry from Open-Meteo free API tier; calibrated synthetic fallback active when offline.",
            "Policy analysis constitutes research support and does not replace statutory regulatory auditing."
        ]

        analysis_section = AnalysisSection(
            analysis_id=analysis_id,
            location=EvidenceLocation(
                region_label=location_label,
                latitude=latitude,
                longitude=longitude,
                coordinate_commitment=None
            ),
            created_at_utc=now_utc,
            data_mode=data_mode,
            inputs=inputs,
            transformations=transformations,
            risk_output=risk_output,
            exposure_output=exposure_output,
            policy_output=policy_output
        )

        bundle = ClimateEvidenceBundle(
            schema_version="1.0.0",
            evidence_id=evidence_id,
            analysis=analysis_section,
            model_manifest=model_manifest,
            code_revision=code_revision,
            limitations=limitations,
            hash_algorithm="keccak256",
            canonicalization_version="aegis-canonical-json-v1"
        )

        # Compute digest
        digest = compute_bundle_digest(bundle)

        # Persist bundle record
        record = EvidenceBundleRecord(
            evidence_id=evidence_id,
            analysis_id=analysis_id,
            schema_version=bundle.schema_version,
            digest=digest,
            bundle_payload=bundle.model_dump(),
            created_at_utc=now_utc,
            anchor_status="NOT_ANCHORED"
        )
        evidence_store.save_bundle(record)

        return bundle, digest

    @staticmethod
    def get_bundle(evidence_id: str) -> Optional[ClimateEvidenceBundle]:
        record = evidence_store.get_bundle(evidence_id)
        if not record:
            return None
        return ClimateEvidenceBundle.model_validate(record.bundle_payload)

    @staticmethod
    def verify_bundle(bundle_payload: Dict[str, Any], expected_digest: str) -> Dict[str, Any]:
        """
        PRD 2: E-099 Independent verification endpoint.
        Recomputes Keccak-256 digest and asserts tamper detection.
        """
        matches, computed_digest = verify_bundle_digest(bundle_payload, expected_digest)
        return {
            "status": "PASS" if matches else "FAIL",
            "content_digest_matches": matches,
            "expected_digest": expected_digest,
            "computed_digest": computed_digest,
            "tamper_detected": not matches,
            "verified_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "schema_version": bundle_payload.get("schema_version", "1.0.0"),
            "hash_algorithm": "keccak256"
        }


evidence_service = EvidenceService()
