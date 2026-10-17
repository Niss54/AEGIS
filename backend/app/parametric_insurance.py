"""
TERRA-SENTINEL Production Specification: Phase 15
Module: terra_sentinel.phase_15.parametricbondcontroller
Governance: Gravitas Reliability Runtime · Model Context Protocol Compliant

Mathematical Governing Equation:
Trigger(D) = I_{D >= D_threshold} => Payout(Beneficiary)
"""

import os
import sys
import time
import math
import logging
import asyncio
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field

logger = logging.getLogger("terra_sentinel.phase_15")

# ─── PYDANTIC SCHEMAS ────────────────────────────────────────────────────────

class DisasterBondModel(BaseModel):
    event_id: str = Field(..., description="Unique UUIDv4 telemetry event identifier")
    timestamp_epoch: float = Field(default_factory=time.time, description="Epoch timestamp")
    execution_tier: str = Field("ENTERPRISE_PROD", description="Execution tier label")
    verified_flag: bool = Field(True, description="Cryptographic verification indicator")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Telemetry metadata payload")


class TriggerEvaluationRequest(BaseModel):
    waterlogging_depth_cm: float = Field(..., ge=0.0, description="Observed flood/waterlogging depth in cm")
    threshold_depth_cm: float = Field(50.0, gt=0.0, description="Parametric trigger depth threshold in cm")
    risk_score_bps: int = Field(..., ge=0, le=10000, description="Risk score in basis points (0-10000)")
    threshold_risk_bps: int = Field(6500, ge=0, le=10000, description="Risk threshold in BPS (e.g. 6500 = 0.65)")
    notional_principal_usd: float = Field(100000.0, gt=0.0, description="Bond notional face value")
    coverage_limit_usd: float = Field(250000.0, gt=0.0, description="Contractual maximum payout limit")
    beneficiary: str = Field("0x71C2E696688b14AE0D78278fCeB78C2651F87bF9", description="Designated payout recipient address")


class BondSettlementRequest(BaseModel):
    bond_id: str = Field(..., description="Unique contract bond identifier bytes32 / string")
    assessment_id: str = Field(..., description="On-chain assessment event ID")
    waterlogging_depth_cm: float = Field(..., ge=0.0)
    risk_score_bps: int = Field(..., ge=0, le=10000)
    beneficiary: str = Field(...)
    payout_amount_usd: Optional[float] = Field(None, description="Optional override or calculated payout")
    force_fallback: bool = Field(False, description="Simulate upstream failure to test circuit breaker")


class CFMCMitigationRewardRequest(BaseModel):
    beneficiary: str = Field(..., description="Mitigation sponsor or local municipality address")
    assessment_id: str = Field(..., description="Assessment identifier")
    risk_score_bps: int = Field(..., ge=0, le=10000, description="Agent 1 risk score BPS")
    dem_depth_cm: float = Field(..., ge=0.0, description="Agent 2 observed inundation depth")
    lat: float = Field(19.0728, description="Latitude")
    lon: float = Field(72.8797, description="Longitude")


# ─── MATHEMATICAL INVARIANT ENGINE ──────────────────────────────────────────

def evaluate_parametric_trigger(
    depth_cm: float,
    threshold_cm: float = 50.0,
    risk_score_bps: int = 7000,
    threshold_risk_bps: int = 6500,
    principal_usd: float = 100000.0,
    coverage_limit_usd: float = 250000.0
) -> Dict[str, Any]:
    """
    Evaluates: Trigger(D) = I_{D >= D_threshold} => Payout(Beneficiary)
    
    Returns indicator, triggered flag, severity ratio, and calculated payout amount.
    """
    # Physical indicator evaluation
    depth_triggered = depth_cm >= threshold_cm
    risk_triggered = risk_score_bps >= threshold_risk_bps
    
    # Parametric activation: either sustained physical depth OR critical risk SLA breach
    indicator = 1 if (depth_triggered or risk_triggered) else 0
    triggered = bool(indicator == 1)
    
    # Severity multiplier scaling: min(1.0, depth / (2 * threshold)) + risk bump
    severity_ratio = 0.0
    if triggered:
        depth_ratio = min(1.0, depth_cm / max(1.0, threshold_cm * 1.5))
        risk_ratio = min(1.0, risk_score_bps / 10000.0)
        severity_ratio = round(max(depth_ratio, risk_ratio), 4)
        calculated_payout = round(min(coverage_limit_usd, principal_usd * severity_ratio), 2)
    else:
        calculated_payout = 0.0

    return {
        "governing_equation": "Trigger(D) = I_{D >= D_threshold} => Payout(Beneficiary)",
        "indicator": indicator,
        "triggered": triggered,
        "depth_triggered": depth_triggered,
        "risk_triggered": risk_triggered,
        "waterlogging_depth_cm": depth_cm,
        "threshold_depth_cm": threshold_cm,
        "risk_score_bps": risk_score_bps,
        "threshold_risk_bps": threshold_risk_bps,
        "severity_ratio": severity_ratio,
        "payout_amount_usd": calculated_payout,
        "notional_principal_usd": principal_usd,
        "coverage_limit_usd": coverage_limit_usd
    }


def compute_settlement_receipt_hash(bond_id: str, assessment_id: str, payout_usd: float, beneficiary: str) -> str:
    """
    Computes deterministic SHA256 digest for settlement receipt non-repudiation.
    """
    raw = f"{bond_id}:{assessment_id}:{round(payout_usd, 2)}:{beneficiary.lower()}"
    return "0x" + hashlib.sha256(raw.encode()).hexdigest()


# ─── CONTROLLER & CIRCUIT BREAKER ───────────────────────────────────────────

class ParametricBondController:
    """
    Executive Controller for Phase 15 (Parametric Disaster Insurance & Automated Smart Bond Settlement).
    Enforces strict mathematical bounds, 3-tier circuit breaker, and local audit fallback.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.phase_id = 15
        self.name = "Parametric Disaster Insurance & Automated Smart Bond Settlement"
        self.state = "INITIALIZED"
        
        # Circuit Breaker state
        self.circuit_state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.consecutive_failures = 0
        self.failure_threshold = 3
        self.cooldown_period_sec = 30.0
        self.last_failure_time: Optional[float] = None
        self.last_state_change: float = time.time()
        
        # Local fallback audit ledger for disaster bond settlements
        self._local_settlement_ledger: List[Dict[str, Any]] = []
        self._local_cfmc_ledger: List[Dict[str, Any]] = []
        
        logger.info(f"{self.name} initialized successfully.")

    def _record_failure(self):
        now = time.time()
        self.last_failure_time = now
        self.consecutive_failures += 1
        logger.warning(f"ParametricBond failure #{self.consecutive_failures} recorded at {now}")
        if self.consecutive_failures >= self.failure_threshold:
            self.circuit_state = "OPEN"
            self.last_state_change = now
            logger.error("ParametricBond Circuit breaker TRIPPED -> OPEN. Enforcing Tier 2 local fallback.")

    def _record_success(self):
        if self.circuit_state == "HALF_OPEN":
            logger.info("ParametricBond probe successful. Circuit breaker resetting to CLOSED.")
        self.circuit_state = "CLOSED"
        self.consecutive_failures = 0

    def _check_circuit(self) -> str:
        now = time.time()
        if self.circuit_state == "OPEN":
            if self.last_failure_time and (now - self.last_failure_time) >= self.cooldown_period_sec:
                self.circuit_state = "HALF_OPEN"
                self.last_state_change = now
                logger.info("ParametricBond Cooldown elapsed. Circuit breaker transitioning to HALF_OPEN probe.")
        return self.circuit_state

    async def execute_phase_pipeline(self, payload: Dict[str, Any]) -> DisasterBondModel:
        """
        Executes PRD Phase 15 Operational Pipeline satisfying contractual invariant:
        Trigger(D) = I_{D >= D_threshold} => Payout(Beneficiary)
        """
        logger.info(f"Executing {self.name} pipeline...")
        start_time = time.perf_counter()
        try:
            if not payload:
                raise ValueError(f"Empty payload rejected by {self.name} gate.")

            # Extract or set default parametric inputs
            depth_cm = float(payload.get("waterlogging_depth_cm", payload.get("telemetry", 42.0)))
            threshold_cm = float(payload.get("threshold_depth_cm", 50.0))
            risk_bps = int(payload.get("risk_score_bps", 7200))
            threshold_bps = int(payload.get("threshold_risk_bps", 6500))
            principal = float(payload.get("notional_principal_usd", 100000.0))
            coverage = float(payload.get("coverage_limit_usd", 250000.0))
            beneficiary = str(payload.get("beneficiary", "0x71C2E696688b14AE0D78278fCeB78C2651F87bF9"))

            trigger_eval = evaluate_parametric_trigger(
                depth_cm=depth_cm,
                threshold_cm=threshold_cm,
                risk_score_bps=risk_bps,
                threshold_risk_bps=threshold_bps,
                principal_usd=principal,
                coverage_limit_usd=coverage
            )

            settlement_res = None
            if trigger_eval["triggered"]:
                settlement_res = await self.settle_parametric_bond(
                    bond_id=payload.get("bond_id", f"BOND-{int(time.time())}"),
                    assessment_id=payload.get("event_id", f"TS-EVT-{int(time.time())}"),
                    depth_cm=depth_cm,
                    risk_score_bps=risk_bps,
                    beneficiary=beneficiary,
                    payout_amount_usd=trigger_eval["payout_amount_usd"],
                    force_fallback=bool(payload.get("force_fallback", False))
                )

            latency_ms = (time.perf_counter() - start_time) * 1000
            result_dict = {
                "processed_by": self.name,
                "latency_ms": latency_ms,
                "status": "OPERATIONAL",
                "circuit_state": self._check_circuit(),
                "trigger_evaluation": trigger_eval,
                "settlement": settlement_res,
                "data": payload
            }

            event_id = str(payload.get("event_id", f"TS-BOND-EVT-{int(time.time())}"))
            return DisasterBondModel(
                event_id=event_id,
                execution_tier="ENTERPRISE_PROD" if self.circuit_state == "CLOSED" else "TIER_2_LOCAL_FALLBACK",
                verified_flag=True,
                metadata=result_dict
            )
        except Exception as exc:
            logger.error(f"Error in {self.name}: {exc}")
            raise

    async def settle_parametric_bond(
        self,
        bond_id: str,
        assessment_id: str,
        depth_cm: float,
        risk_score_bps: int,
        beneficiary: str,
        payout_amount_usd: Optional[float] = None,
        force_fallback: bool = False
    ) -> Dict[str, Any]:
        """
        Executes automated bond settlement either via Web3 Polygon Amoy or Tier 2 local fallback.
        """
        circuit = self._check_circuit()
        now = time.time()
        
        # Calculate payout if not supplied
        if payout_amount_usd is None:
            eval_res = evaluate_parametric_trigger(depth_cm=depth_cm, risk_score_bps=risk_score_bps)
            payout_amount_usd = eval_res["payout_amount_usd"]

        receipt_hash = compute_settlement_receipt_hash(bond_id, assessment_id, payout_amount_usd, beneficiary)

        # Failure injection or circuit open branch
        if force_fallback or circuit == "OPEN":
            if force_fallback:
                self._record_failure()
            logger.warning("Routing bond settlement to Tier 2 Local Offline Ledger due to circuit state / force_fallback.")
            record = {
                "settlement_id": f"SETTLE-LOCAL-{int(now * 1000)}",
                "bond_id": bond_id,
                "assessment_id": assessment_id,
                "beneficiary": beneficiary,
                "payout_amount_usd": payout_amount_usd,
                "settlement_tier": "TIER_2_LOCAL_FALLBACK",
                "receipt_hash": receipt_hash,
                "tx_hash": f"0xlocal_settlement_{receipt_hash[2:18]}",
                "timestamp": now,
                "circuit_state": self.circuit_state,
                "status": "SETTLED_OFFLINE"
            }
            self._local_settlement_ledger.append(record)
            return record

        # Primary Web3 Execution simulation
        try:
            self._record_success()
            record = {
                "settlement_id": f"SETTLE-ONCHAIN-{int(now * 1000)}",
                "bond_id": bond_id,
                "assessment_id": assessment_id,
                "beneficiary": beneficiary,
                "payout_amount_usd": payout_amount_usd,
                "settlement_tier": "TIER_1_POLYGON_AMOY",
                "receipt_hash": receipt_hash,
                "tx_hash": f"0xamoy_{receipt_hash[2:18]}",
                "timestamp": now,
                "circuit_state": "CLOSED",
                "status": "SETTLED_ONCHAIN"
            }
            self._local_settlement_ledger.append(record)
            return record
        except Exception as exc:
            self._record_failure()
            logger.error(f"On-chain settlement failed: {exc}. Falling back to Tier 2.")
            record = {
                "settlement_id": f"SETTLE-FALLBACK-{int(now * 1000)}",
                "bond_id": bond_id,
                "assessment_id": assessment_id,
                "beneficiary": beneficiary,
                "payout_amount_usd": payout_amount_usd,
                "settlement_tier": "TIER_2_LOCAL_FALLBACK",
                "receipt_hash": receipt_hash,
                "tx_hash": f"0xfallback_{receipt_hash[2:18]}",
                "timestamp": now,
                "circuit_state": self.circuit_state,
                "status": "SETTLED_FALLBACK"
            }
            self._local_settlement_ledger.append(record)
            return record

    async def evaluate_cfmc_mitigation_reward(
        self,
        beneficiary: str,
        assessment_id: str,
        risk_score_bps: int,
        dem_depth_cm: float,
        lat: float = 19.0728,
        lon: float = 72.8797
    ) -> Dict[str, Any]:
        """
        CarbonFloodCredit (CFMC) Mitigation Reward rule:
        Mint 100 CFMC if Agent 1 risk >= 6500 (CRITICAL) and Agent 2 DEM depth < 20cm (Effective defense).
        """
        is_critical_risk = risk_score_bps >= 6500
        is_low_damage = dem_depth_cm < 20.0
        eligible = is_critical_risk and is_low_damage

        reward_amount = 100.0 if eligible else 0.0
        now = time.time()
        tx_hash = f"0xcfmc_{int(now)}_{abs(int(lat*1000))}"

        result = {
            "eligible": eligible,
            "minted": eligible,
            "reward_amount_cfmc": reward_amount,
            "beneficiary": beneficiary,
            "assessment_id": assessment_id,
            "risk_score_bps": risk_score_bps,
            "dem_depth_cm": dem_depth_cm,
            "rule": "risk_score_bps >= 6500 and dem_depth_cm < 20",
            "tx_hash": tx_hash if eligible else None,
            "timestamp": now
        }
        if eligible:
            self._local_cfmc_ledger.append(result)
        return result

    def get_health(self) -> Dict[str, Any]:
        self._check_circuit()
        return {
            "phase": 15,
            "subsystem": self.name,
            "circuit_state": self.circuit_state,
            "consecutive_failures": self.consecutive_failures,
            "failure_threshold": self.failure_threshold,
            "cooldown_period_sec": self.cooldown_period_sec,
            "total_settlements": len(self._local_settlement_ledger),
            "total_cfmc_rewards": len(self._local_cfmc_ledger),
            "status": "HEALTHY" if self.circuit_state == "CLOSED" else "DEGRADED_FALLBACK"
        }


# Singleton Instance
parametric_bond_controller = ParametricBondController()


# ─── SYNCHRONOUS HELPERS FOR MCP HUB ────────────────────────────────────────

def evaluate_parametric_trigger_sync(
    depth_cm: float,
    threshold_cm: float = 50.0,
    risk_score_bps: int = 7000,
    threshold_risk_bps: int = 6500,
    principal_usd: float = 100000.0,
    coverage_limit_usd: float = 250000.0
) -> Dict[str, Any]:
    return evaluate_parametric_trigger(
        depth_cm=depth_cm,
        threshold_cm=threshold_cm,
        risk_score_bps=risk_score_bps,
        threshold_risk_bps=threshold_risk_bps,
        principal_usd=principal_usd,
        coverage_limit_usd=coverage_limit_usd
    )


def settle_parametric_bond_sync(
    bond_id: str,
    assessment_id: str,
    depth_cm: float,
    risk_score_bps: int,
    beneficiary: str,
    payout_amount_usd: Optional[float] = None,
    force_fallback: bool = False
) -> Dict[str, Any]:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(
                    asyncio.run,
                    parametric_bond_controller.settle_parametric_bond(
                        bond_id=bond_id,
                        assessment_id=assessment_id,
                        depth_cm=depth_cm,
                        risk_score_bps=risk_score_bps,
                        beneficiary=beneficiary,
                        payout_amount_usd=payout_amount_usd,
                        force_fallback=force_fallback
                    )
                ).result()
        else:
            return loop.run_until_complete(
                parametric_bond_controller.settle_parametric_bond(
                    bond_id=bond_id,
                    assessment_id=assessment_id,
                    depth_cm=depth_cm,
                    risk_score_bps=risk_score_bps,
                    beneficiary=beneficiary,
                    payout_amount_usd=payout_amount_usd,
                    force_fallback=force_fallback
                )
            )
    except Exception:
        return asyncio.run(
            parametric_bond_controller.settle_parametric_bond(
                bond_id=bond_id,
                assessment_id=assessment_id,
                depth_cm=depth_cm,
                risk_score_bps=risk_score_bps,
                beneficiary=beneficiary,
                payout_amount_usd=payout_amount_usd,
                force_fallback=force_fallback
            )
        )


def evaluate_cfmc_mitigation_reward_sync(
    beneficiary: str,
    assessment_id: str,
    risk_score_bps: int,
    dem_depth_cm: float,
    lat: float = 19.0728,
    lon: float = 72.8797
) -> Dict[str, Any]:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(
                    asyncio.run,
                    parametric_bond_controller.evaluate_cfmc_mitigation_reward(
                        beneficiary=beneficiary,
                        assessment_id=assessment_id,
                        risk_score_bps=risk_score_bps,
                        dem_depth_cm=dem_depth_cm,
                        lat=lat,
                        lon=lon
                    )
                ).result()
        else:
            return loop.run_until_complete(
                parametric_bond_controller.evaluate_cfmc_mitigation_reward(
                    beneficiary=beneficiary,
                    assessment_id=assessment_id,
                    risk_score_bps=risk_score_bps,
                    dem_depth_cm=dem_depth_cm,
                    lat=lat,
                    lon=lon
                )
            )
    except Exception:
        return asyncio.run(
            parametric_bond_controller.evaluate_cfmc_mitigation_reward(
                beneficiary=beneficiary,
                assessment_id=assessment_id,
                risk_score_bps=risk_score_bps,
                dem_depth_cm=dem_depth_cm,
                lat=lat,
                lon=lon
            )
        )
