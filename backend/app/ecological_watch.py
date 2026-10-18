"""
TERRA-SENTINEL: Sentinel Flood-Watch Ecological Encroachment & Wetland Threat Engine
Phase 30.4: Multi-Temporal Remote Sensing Change Detection (NDBI, MNDWI, NDVI) & Ecological Threat Index (ETI)
Synthesized from Hou-dini/sentinel-flood-watch (Google Cloud Rapid Agent Hackathon Winner)
"""

import math
import logging
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field

logger = logging.getLogger("terra_sentinel.ecological_watch")


class EcologicalThreatTier(str, Enum):
    STABLE_ECOLOGICAL_BUFFER = "STABLE_ECOLOGICAL_BUFFER"
    MODERATE_ALTERATION = "MODERATE_ALTERATION"
    HIGH_RISK_CLEARANCE = "HIGH_RISK_CLEARANCE"
    CRITICAL_ENCROACHMENT = "CRITICAL_ENCROACHMENT"


class EcologicalSiteCategory(str, Enum):
    MANGROVE_CRZ = "MANGROVE_CRZ"            # Coastal Regulation Zone 1A
    RAMSAR_WETLAND = "RAMSAR_WETLAND"        # Protected Ramsar Wetland
    RIVERINE_FLOODPLAIN = "RIVERINE_FLOODPLAIN"  # Active River Buffer
    URBAN_RIPARIAN = "URBAN_RIPARIAN"        # Urban Lake Catchment Buffer


class EcologicalSiteProfile(BaseModel):
    site_id: str
    site_name: str
    category: EcologicalSiteCategory
    location_name: str
    state: str
    latitude: float
    longitude: float
    buffer_radius_km: float
    baseline_ndbi: float   # Concrete / Built-up index at t0
    baseline_ndvi: float   # Vegetation canopy index at t0
    baseline_mndwi: float  # Wetland water index at t0
    protected_status: str


class EcologicalScanRequest(BaseModel):
    site_id: str = Field(default="site_mithi_mangrove", description="Target ecological site ID")
    current_ndbi: Optional[float] = Field(default=None, ge=-1.0, le=1.0, description="Observed Sentinel-2 NDBI at t1")
    current_ndvi: Optional[float] = Field(default=None, ge=-1.0, le=1.0, description="Observed Sentinel-2 NDVI at t1")
    current_mndwi: Optional[float] = Field(default=None, ge=-1.0, le=1.0, description="Observed Sentinel-2 MNDWI at t1")
    notes: Optional[str] = Field(default="", description="Observer or mission telemetry notes")


class EcologicalScanResult(BaseModel):
    site_id: str
    site_name: str
    category: EcologicalSiteCategory
    location_name: str
    latitude: float
    longitude: float
    baseline_ndbi: float
    baseline_ndvi: float
    baseline_mndwi: float
    current_ndbi: float
    current_ndvi: float
    current_mndwi: float
    delta_ndbi: float
    delta_ndvi: float
    delta_mndwi: float
    eti_score: float
    threat_tier: EcologicalThreatTier
    concrete_expansion_detected: bool
    vegetation_loss_detected: bool
    wetland_shrinkage_detected: bool
    enforcement_recommendation: str
    governing_invariant: str
    scanned_at: str


class SentinelFloodWatchEngine:
    """
    Sentinel Flood-Watch Multi-Temporal Encroachment Engine.
    Detects illegal concrete expansion, mangrove clearing, and wetland shrinkage
    across vital ecological sponge zones using Sentinel-2 MSI spectral differences.
    """

    def __init__(self):
        self._sites_catalog: Dict[str, EcologicalSiteProfile] = {
            "site_mithi_mangrove": EcologicalSiteProfile(
                site_id="site_mithi_mangrove",
                site_name="Mahim Nature Park & Mithi River Estuary",
                category=EcologicalSiteCategory.MANGROVE_CRZ,
                location_name="Bandra-Kurla Complex (BKC) Estuary Buffer, Mumbai",
                state="Maharashtra",
                latitude=19.0520,
                longitude=72.8610,
                buffer_radius_km=2.5,
                baseline_ndbi=-0.15,
                baseline_ndvi=0.62,
                baseline_mndwi=0.35,
                protected_status="CRZ-1A Ecologically Sensitive Zone"
            ),
            "site_bellandur_wetland": EcologicalSiteProfile(
                site_id="site_bellandur_wetland",
                site_name="Bellandur Lake Wetland Buffer Zone",
                category=EcologicalSiteCategory.URBAN_RIPARIAN,
                location_name="Bellandur-Varthur Wetland Network, Bengaluru",
                state="Karnataka",
                latitude=12.9372,
                longitude=77.6744,
                buffer_radius_km=1.8,
                baseline_ndbi=-0.08,
                baseline_ndvi=0.54,
                baseline_mndwi=0.42,
                protected_status="NGT 75m Riparian Buffer Mandate"
            ),
            "site_yamuna_oza": EcologicalSiteProfile(
                site_id="site_yamuna_oza",
                site_name="Yamuna Khadar Biodiversity Zone",
                category=EcologicalSiteCategory.RIVERINE_FLOODPLAIN,
                location_name="Yamuna Bank Active Inundation Plain, Delhi",
                state="Delhi NCR",
                latitude=28.6250,
                longitude=77.2650,
                buffer_radius_km=3.0,
                baseline_ndbi=-0.22,
                baseline_ndvi=0.58,
                baseline_mndwi=0.38,
                protected_status="O-Zone Yamuna Rejuvenation Plan"
            ),
            "site_deepor_beel": EcologicalSiteProfile(
                site_id="site_deepor_beel",
                site_name="Deepor Beel Ramsar Wetland",
                category=EcologicalSiteCategory.RAMSAR_WETLAND,
                location_name="South of Brahmaputra River, Guwahati",
                state="Assam",
                latitude=26.1280,
                longitude=91.6620,
                buffer_radius_km=4.0,
                baseline_ndbi=-0.30,
                baseline_ndvi=0.68,
                baseline_mndwi=0.55,
                protected_status="Ramsar Site No. 1207"
            ),
            "site_pallikaranai_marsh": EcologicalSiteProfile(
                site_id="site_pallikaranai_marsh",
                site_name="Pallikaranai Marsh Reserve Forest",
                category=EcologicalSiteCategory.RAMSAR_WETLAND,
                location_name="South Chennai Coastal Plain, Chennai",
                state="Tamil Nadu",
                latitude=12.9350,
                longitude=80.2180,
                buffer_radius_km=3.5,
                baseline_ndbi=-0.18,
                baseline_ndvi=0.60,
                baseline_mndwi=0.48,
                protected_status="Ramsar Site No. 2484"
            )
        }
        self._active_threats: List[EcologicalScanResult] = []

    def list_sites(self) -> List[EcologicalSiteProfile]:
        """Returns list of all preloaded ecological sites."""
        return list(self._sites_catalog.values())

    def get_site(self, site_id: str) -> Optional[EcologicalSiteProfile]:
        """Retrieves site profile by ID."""
        return self._sites_catalog.get(site_id)

    def calculate_eti(
        self,
        delta_ndbi: float,
        delta_ndvi: float,
        delta_mndwi: float
    ) -> float:
        """
        Governing Invariant:
        ETI = 0.45 * max(0, Delta_NDBI) + 0.35 * max(0, -Delta_NDVI) + 0.20 * max(0, -Delta_MNDWI)
        Clamped to [0.0, 1.0].
        """
        encroachment_component = 0.45 * max(0.0, delta_ndbi)
        vegetation_loss_component = 0.35 * max(0.0, -delta_ndvi)
        water_shrinkage_component = 0.20 * max(0.0, -delta_mndwi)

        raw_eti = encroachment_component + vegetation_loss_component + water_shrinkage_component
        return round(min(1.0, max(0.0, raw_eti)), 4)

    def classify_threat_tier(self, eti_score: float) -> Tuple[EcologicalThreatTier, str]:
        """Classifies ETI into threat tiers and assigns enforcement actions."""
        if eti_score >= 0.60:
            return (
                EcologicalThreatTier.CRITICAL_ENCROACHMENT,
                "URGENT: Immediate MoEFCC / Coastal Zone Management Authority enforcement dispatch. Stop-work notice issued."
            )
        elif eti_score >= 0.40:
            return (
                EcologicalThreatTier.HIGH_RISK_CLEARANCE,
                "HIGH: Embankment or concrete landfilling detected. Drone reconnaissance flight and municipal inspection mandated."
            )
        elif eti_score >= 0.20:
            return (
                EcologicalThreatTier.MODERATE_ALTERATION,
                "ELEVATED: Canopy thinning or seasonal boundary shrinkage detected. Increase satellite re-visit cadence."
            )
        else:
            return (
                EcologicalThreatTier.STABLE_ECOLOGICAL_BUFFER,
                "NORMAL: Ecological sponge buffer intact. Natural hydrological retention maintained."
            )

    def scan_site(self, req: EcologicalScanRequest) -> EcologicalScanResult:
        """
        Executes multi-temporal satellite encroachment scan:
        1. Resolve baseline spectral metrics
        2. Ingest observed Sentinel-2 spectral rasters (or simulated satellite telemetry)
        3. Quantify Delta_NDBI, Delta_NDVI, Delta_MNDWI
        4. Compute Ecological Threat Index (ETI)
        5. Assign threat tier and legal compliance recommendation
        """
        site = self.get_site(req.site_id)
        if not site:
            # Resilient fallback default for arbitrary coordinate or new reserve
            site = EcologicalSiteProfile(
                site_id=req.site_id,
                site_name=f"Ecological Site ({req.site_id})",
                category=EcologicalSiteCategory.MANGROVE_CRZ,
                location_name="General Planetary Buffer Corridor",
                state="Bharat Ecological Territory",
                latitude=19.0760,
                longitude=72.8777,
                buffer_radius_km=2.0,
                baseline_ndbi=-0.15,
                baseline_ndvi=0.60,
                baseline_mndwi=0.40,
                protected_status="Statutory Protected Environmental Zone"
            )

        # Ingest current spectral values or simulate nominal variation
        curr_ndbi = req.current_ndbi if req.current_ndbi is not None else site.baseline_ndbi + 0.05
        curr_ndvi = req.current_ndvi if req.current_ndvi is not None else site.baseline_ndvi - 0.04
        curr_mndwi = req.current_mndwi if req.current_mndwi is not None else site.baseline_mndwi - 0.03

        delta_ndbi = round(curr_ndbi - site.baseline_ndbi, 4)
        delta_ndvi = round(curr_ndvi - site.baseline_ndvi, 4)
        delta_mndwi = round(curr_mndwi - site.baseline_mndwi, 4)

        eti_score = self.calculate_eti(delta_ndbi, delta_ndvi, delta_mndwi)
        tier, recommendation = self.classify_threat_tier(eti_score)

        result = EcologicalScanResult(
            site_id=site.site_id,
            site_name=site.site_name,
            category=site.category,
            location_name=site.location_name,
            latitude=site.latitude,
            longitude=site.longitude,
            baseline_ndbi=site.baseline_ndbi,
            baseline_ndvi=site.baseline_ndvi,
            baseline_mndwi=site.baseline_mndwi,
            current_ndbi=curr_ndbi,
            current_ndvi=curr_ndvi,
            current_mndwi=curr_mndwi,
            delta_ndbi=delta_ndbi,
            delta_ndvi=delta_ndvi,
            delta_mndwi=delta_mndwi,
            eti_score=eti_score,
            threat_tier=tier,
            concrete_expansion_detected=delta_ndbi > 0.05,
            vegetation_loss_detected=delta_ndvi < -0.05,
            wetland_shrinkage_detected=delta_mndwi < -0.05,
            enforcement_recommendation=recommendation,
            governing_invariant="ETI = 0.45 * max(0, Delta_NDBI) + 0.35 * max(0, -Delta_NDVI) + 0.20 * max(0, -Delta_MNDWI)",
            scanned_at=datetime.now(timezone.utc).isoformat()
        )

        # Cache threat if elevated
        if tier != EcologicalThreatTier.STABLE_ECOLOGICAL_BUFFER:
            self._active_threats.append(result)
            # Keep latest 50
            if len(self._active_threats) > 50:
                self._active_threats.pop(0)

        return result

    def get_active_threats(self) -> List[EcologicalScanResult]:
        """Returns list of active detected violations."""
        return self._active_threats


# Singleton instance
ecological_watch_engine = SentinelFloodWatchEngine()
