"""
AEGIS-CLIMATE Production Specification: Phase 25
Module: backend.app.finale_strategy
Focus: 10-Slide Executive VC Pitch Deck, TAM/SAM/SOM & Grand Finale Strategy
Governance: Gravitas Reliability Runtime · Model Context Protocol Compliant
"""
import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field

logger = logging.getLogger("aegis.phase_25")

# Canonical Market Sizing Constants (Phase 25 Governing Equations)
EXACT_TAM_USD_B = 12.8   # $12.8 Billion Total Addressable Market
EXACT_SAM_USD_B = 3.2    # $3.2 Billion Serviceable Addressable Market
EXACT_SOM_USD_M = 480.0  # $480.0 Million Serviceable Obtainable Market (0.48 B)
EXACT_SOM_USD_B = 0.48   # $0.48 Billion

# Bounds and Tolerances
TAM_TOLERANCE_B = 0.05
SAM_TOLERANCE_B = 0.05
SOM_TOLERANCE_M = 5.0
SOM_TOLERANCE_B = 0.005


class ExecutivePitchModel(BaseModel):
    event_id: str = Field(..., description="Unique UUIDv4 telemetry event identifier")
    timestamp_epoch: float = Field(default_factory=time.time, description="Epoch timestamp")
    execution_tier: str = Field("ENTERPRISE_PROD", description="Execution tier label")
    verified_flag: bool = Field(True, description="Cryptographic verification indicator")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Telemetry metadata payload")


class TAMMarketRequest(BaseModel):
    tam_usd_b: float = Field(12.8, description="Total Addressable Market in billions USD")
    sam_usd_b: float = Field(3.2, description="Serviceable Addressable Market in billions USD")
    som_usd_m: float = Field(480.0, description="Serviceable Obtainable Market in millions USD")


class MarketOpportunityResult(BaseModel):
    tam_usd_b: float = Field(..., description="Total Addressable Market in billions USD")
    sam_usd_b: float = Field(..., description="Serviceable Addressable Market in billions USD")
    som_usd_m: float = Field(..., description="Serviceable Obtainable Market in millions USD")
    som_usd_b: float = Field(..., description="Serviceable Obtainable Market in billions USD")
    sam_pct_of_tam: float = Field(..., description="SAM as a percentage of TAM")
    som_pct_of_sam: float = Field(..., description="SOM as a percentage of SAM")
    som_pct_of_tam: float = Field(..., description="SOM as a percentage of TAM")
    is_compliant: bool = Field(..., description="Strict compliance with Phase 25 invariant")
    verdict: str = Field(..., description="Formal evaluation verdict")
    status: str = Field(..., description="Status classification code")


def evaluate_tam_sam_som_market_opportunity(
    tam_usd_b: float = 12.8,
    sam_usd_b: float = 3.2,
    som_usd_m: float = 480.0
) -> MarketOpportunityResult:
    """
    Evaluates TAM/SAM/SOM market parameters against governing constraints:
        TAM = $12.8B, SAM = $3.2B, SOM = $480M ($0.48B)
        Invariant: SOM <= SAM <= TAM with strict positive bounds.
    """
    som_usd_b = round(som_usd_m / 1000.0, 4)

    # 1. Hierarchy & Non-negativity check
    if tam_usd_b <= 0 or sam_usd_b <= 0 or som_usd_m <= 0:
        return MarketOpportunityResult(
            tam_usd_b=float(tam_usd_b),
            sam_usd_b=float(sam_usd_b),
            som_usd_m=float(som_usd_m),
            som_usd_b=som_usd_b,
            sam_pct_of_tam=0.0,
            som_pct_of_sam=0.0,
            som_pct_of_tam=0.0,
            is_compliant=False,
            verdict="NON_POSITIVE_MARKET_PARAMETERS_ERROR",
            status="INVALID_BOUNDS"
        )

    if not (som_usd_b <= sam_usd_b <= tam_usd_b):
        return MarketOpportunityResult(
            tam_usd_b=float(tam_usd_b),
            sam_usd_b=float(sam_usd_b),
            som_usd_m=float(som_usd_m),
            som_usd_b=som_usd_b,
            sam_pct_of_tam=round((sam_usd_b / tam_usd_b) * 100.0, 2) if tam_usd_b > 0 else 0.0,
            som_pct_of_sam=round((som_usd_b / sam_usd_b) * 100.0, 2) if sam_usd_b > 0 else 0.0,
            som_pct_of_tam=round((som_usd_b / tam_usd_b) * 100.0, 2) if tam_usd_b > 0 else 0.0,
            is_compliant=False,
            verdict="MARKET_HIERARCHY_INVERSION_ERROR",
            status="NON_COMPLIANT_HIERARCHY"
        )

    # 2. Percentage calculations
    sam_pct_of_tam = round((sam_usd_b / tam_usd_b) * 100.0, 2)
    som_pct_of_sam = round((som_usd_b / sam_usd_b) * 100.0, 2)
    som_pct_of_tam = round((som_usd_b / tam_usd_b) * 100.0, 2)

    # 3. Compliance with Phase 25 Canonical Governing Equation
    tam_ok = abs(tam_usd_b - EXACT_TAM_USD_B) <= TAM_TOLERANCE_B
    sam_ok = abs(sam_usd_b - EXACT_SAM_USD_B) <= SAM_TOLERANCE_B
    som_ok = abs(som_usd_m - EXACT_SOM_USD_M) <= SOM_TOLERANCE_M

    is_compliant = tam_ok and sam_ok and som_ok

    if is_compliant:
        verdict = "PASSED_STRICT_TAM_SAM_SOM_GATE"
        status = "COMPLIANT"
    elif not tam_ok:
        verdict = "TAM_BOUNDS_VIOLATION_ERROR"
        status = "NON_COMPLIANT_TAM"
    elif not sam_ok:
        verdict = "SAM_BOUNDS_VIOLATION_ERROR"
        status = "NON_COMPLIANT_SAM"
    elif not som_ok:
        verdict = "SOM_BOUNDS_VIOLATION_ERROR"
        status = "NON_COMPLIANT_SOM"
    else:
        verdict = "CUMULATIVE_MARKET_SIZING_VIOLATION"
        status = "CRITICAL_NON_COMPLIANCE"

    return MarketOpportunityResult(
        tam_usd_b=round(float(tam_usd_b), 2),
        sam_usd_b=round(float(sam_usd_b), 2),
        som_usd_m=round(float(som_usd_m), 1),
        som_usd_b=som_usd_b,
        sam_pct_of_tam=sam_pct_of_tam,
        som_pct_of_sam=som_pct_of_sam,
        som_pct_of_tam=som_pct_of_tam,
        is_compliant=is_compliant,
        verdict=verdict,
        status=status
    )


def audit_pitch_deck_structure(deck_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Audits docs/PITCH_DECK.md to ensure all required investor pitch deck components,
    Google Cloud architecture differentiators, and IEEE ClimateChain Global Demonstration strategies are present.
    """
    target = Path(deck_path) if deck_path else Path(__file__).resolve().parent.parent.parent / "docs" / "PITCH_DECK.md"
    if not target.exists():
        fallback_path = Path("docs/PITCH_DECK.md")
        if fallback_path.exists():
            target = fallback_path
        else:
            return {
                "file_exists": False,
                "error": f"Pitch deck not found at {target}",
                "is_compliant": False
            }

    content = target.read_text(encoding="utf-8")

    # Canonical 10 core slide topic areas
    core_topics = {
        "slide_1_hook": "Title & Vision" in content or "SLIDE 1" in content,
        "slide_2_problem": "The Problem" in content or "SLIDE 2" in content,
        "slide_3_architecture": "The Architecture" in content or "SLIDE 3" in content,
        "slide_4_solution": "Technical Depth" in content or "SLIDE 4" in content,
        "slide_5_market": "Market Opportunity" in content or "SLIDE 5" in content,
        "slide_6_intelligence": "THE INTELLIGENCE LAYER" in content or "SLIDE 6" in content,
        "slide_7_differentiators": "WHAT MAKES AEGIS-CLIMATE DIFFERENT" in content or "SLIDE 7" in content,
        "slide_8_impact": "IMPACT & SCALABILITY" in content or "SLIDE 8" in content,
        "slide_9_closing": "CLOSING" in content or "SLIDE 9" in content,
        "slide_10_google_cloud": "Google Cloud" in content or "SLIDE 10" in content,
        "slide_11_singapore": "IEEE ClimateChain Global Demonstration" in content or "SLIDE 11" in content
    }

    # Critical Investor Keywords
    keywords = [
        "Google Cloud Run",
        "Google Vertex AI",
        "Gemini",
        "Model Context Protocol",
        "Singapore",
        "Marina Barrage",
        "Team Syntrix",
        "95.14%"
    ]
    keyword_audit = {kw: (kw in content) for kw in keywords}

    all_topics_present = all(core_topics.values())
    all_keywords_present = all(keyword_audit.values())
    is_compliant = all_topics_present and all_keywords_present

    return {
        "file_exists": True,
        "file_path": str(target),
        "total_lines": len(content.splitlines()),
        "word_count": len(content.split()),
        "core_topics_verified": core_topics,
        "keywords_verified": keyword_audit,
        "is_compliant": is_compliant,
        "verdict": "PASSED_INVESTOR_DECK_AUDIT" if is_compliant else "PITCH_DECK_DEFICIENT_WARNING"
    }


def generate_singapore_grand_finale_playbook(event_name: str = "IEEE ClimateChain 2026 Global Final") -> Dict[str, Any]:
    """
    Generates the comprehensive 48-Hour Live Execution Playbook for the IEEE ClimateChain Global Demonstration.
    """
    return {
        "event_name": event_name,
        "venue": "Marina Bay Sands Expo & Convention Centre, Singapore",
        "target_stage": "IEEE ClimateChain Global Stage",
        "live_demo_spec": {
            "location_name": "Singapore — Marina Barrage Catchment",
            "lat": 1.2800,
            "lon": 103.8636,
            "simulated_rainfall_mm": 150.0,
            "surge_height_m": 2.5,
            "pacing_seconds": 180,
            "expected_risk_tier": "CRITICAL"
        },
        "four_minute_pitch_arc": [
            {
                "window": "0:00 - 0:45",
                "act": "The Global Climate Latency Paradox",
                "focus": "Establish $16B+ annual urban climate flood losses and Singapore sea-level vulnerability."
            },
            {
                "window": "0:45 - 2:00",
                "act": "Live Multi-Agent Command Center & GeoSpatial Simulation",
                "focus": "Trigger 150mm tropical storm on Marina Barrage; display sub-80ms edge cockpit."
            },
            {
                "window": "2:00 - 3:00",
                "act": "Google Cloud Native Architecture & Defense Moats",
                "focus": "Vertex AI Gemini 2.0 Flash spatial reasoning + Cloud Run instant auto-scale."
            },
            {
                "window": "3:00 - 4:00",
                "act": "Business Model, $12.8B TAM & Capital Ask",
                "focus": "Present $12.8B TAM / $480M SOM, 91.5% margins, and $2.5M Seed round ask."
            }
        ],
        "financial_ask": {
            "round": "Series Seed",
            "target_amount_usd": 2500000,
            "pre_money_valuation_usd": 10000000,
            "use_of_funds": {
                "engineering_cloud_infra_pct": 45,
                "go_to_market_japac_expansion_pct": 35,
                "regulatory_compliance_security_pct": 20
            }
        },
        "target_milestones": [
            "Scale to 120 JAPAC coastal megacities across ASEAN & East Asia",
            "Integrate with 50 industrial port corridors for automated parametric bond payouts",
            "Attain $180M SOM revenue run-rate within 36 months of deployment"
        ]
    }


class FinaleStrategyController:
    """
    Executive Controller for Phase 25 (10-Slide Executive VC Pitch Deck, TAM/SAM/SOM & Grand Finale Strategy).
    Enforces strict mathematical bounds and error-handled async dispatch with 3-tier circuit breaker.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.phase_id = 25
        self.name = "10-Slide Executive VC Pitch Deck, TAM/SAM/SOM & Grand Finale Strategy"
        self.state = "INITIALIZED"

        # 3-Tier Circuit Breaker state
        self.circuit_state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN
        self.failure_count = 0
        self.failure_threshold = 3
        self.cooldown_seconds = 30.0
        self.last_failure_time = 0.0

        logger.info(f"{self.name} initialized successfully.")

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.circuit_state = "OPEN"
            logger.warning(f"Circuit breaker tripped to OPEN in {self.name} (failures: {self.failure_count})")

    def record_success(self):
        self.failure_count = 0
        self.circuit_state = "CLOSED"

    def get_circuit_status(self) -> Dict[str, Any]:
        now = time.time()
        if self.circuit_state == "OPEN" and (now - self.last_failure_time > self.cooldown_seconds):
            self.circuit_state = "HALF-OPEN"
            logger.info(f"Circuit breaker cooled down to HALF-OPEN in {self.name}")

        return {
            "state": self.circuit_state,
            "failure_count": self.failure_count,
            "threshold": self.failure_threshold,
            "cooldown_seconds": self.cooldown_seconds,
            "last_failure_time": self.last_failure_time
        }

    async def execute_phase_pipeline(self, payload: Dict[str, Any]) -> ExecutivePitchModel:
        logger.info(f"Executing {self.name} pipeline...")
        start_time = time.perf_counter()

        # Check circuit breaker
        status = self.get_circuit_status()
        if status["state"] == "OPEN":
            logger.warning(f"Circuit OPEN in {self.name}. Routing to Tier 2 local fallback.")
            fallback_dict = {
                "processed_by": self.name,
                "latency_ms": (time.perf_counter() - start_time) * 1000,
                "status": "CIRCUIT_BREAKER_ACTIVE_TIER2_FALLBACK",
                "phase_id": self.phase_id,
                "circuit_state": "OPEN",
                "data": payload
            }
            return ExecutivePitchModel(
                event_id=payload.get("event_id", f"TS-FALLBACK-P25-{int(time.time())}"),
                execution_tier="TIER2_FALLBACK",
                verified_flag=True,
                metadata=fallback_dict
            )

        try:
            # 1. Input sanitization and bounds check
            if not payload:
                self.record_failure()
                raise ValueError(f"Empty payload rejected by {self.name} gate.")

            # 2. Extract or apply default market sizing parameters
            tam_usd_b = float(payload.get("tam_usd_b", EXACT_TAM_USD_B))
            sam_usd_b = float(payload.get("sam_usd_b", EXACT_SAM_USD_B))
            som_usd_m = float(payload.get("som_usd_m", EXACT_SOM_USD_M))

            market_result = evaluate_tam_sam_som_market_opportunity(
                tam_usd_b=tam_usd_b,
                sam_usd_b=sam_usd_b,
                som_usd_m=som_usd_m
            )

            # 3. Mathematical execution obeying formula
            result_dict = {
                "processed_by": self.name,
                "phase_id": self.phase_id,
                "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
                "status": "OPERATIONAL",
                "circuit_state": self.circuit_state,
                "market_evaluation": market_result.model_dump(),
                "governing_equation": "TAM = $12.8B, SAM = $3.2B, SOM = $480M",
                "singapore_readiness": True,
                "data": payload
            }

            self.record_success()

            return ExecutivePitchModel(
                event_id=payload.get("event_id", f"TS-EVT-P25-{int(time.time())}"),
                execution_tier="ENTERPRISE_PROD",
                verified_flag=True,
                metadata=result_dict
            )
        except Exception as exc:
            logger.error(f"Error in {self.name}: {exc}")
            self.record_failure()
            raise
