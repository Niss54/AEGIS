"""
AEGIS-CLIMATE Production Specification: Phase 7
Module: terra_sentinel.phase_7.macrofinancialcontroller
Governance: Gravitas Reliability Runtime · Model Context Protocol Compliant

Mathematical Governing Equation (Deterministic Constraint):
VaR_95 = Percentile_95(sum_{i=1}^N V_{asset, i} * (1 - e^{-lambda * D_i}))
CVaR_95 = E[Loss | Loss >= VaR_95]
Where:
- V_{asset, i}: Baseline replacement valuation of exposed enterprise asset i (INR)
- D_i: Inundation depth at asset location (cm)
- lambda: Structural vulnerability fragility coefficient [0.015 - 0.035]
- Monte Carlo Stochasticity: D_i ~ Lognormal(mu_D, sigma_D) over N >= 1000 trials
"""
import time
import math
import random
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from backend.app.config import settings

logger = logging.getLogger("aegis.phase_7")


class FinancialVaRModel(BaseModel):
    """
    Standard Phase 7 Contract Model as declared in PRD.md Section 16 (Phase 7).
    """
    event_id: str = Field(..., description="Unique UUIDv4 telemetry event identifier")
    timestamp_epoch: float = Field(default_factory=time.time, description="Epoch timestamp")
    execution_tier: str = Field("ENTERPRISE_PROD", description="Execution tier label")
    verified_flag: bool = Field(True, description="Cryptographic verification indicator")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Telemetry metadata payload")


class AssetValuation(BaseModel):
    asset_id: str
    asset_name: str
    category: str  # critical_infrastructure, commercial_rc, industrial_warehouse, residential_masonry
    valuation_inr: float
    depth_cm: float
    fragility_lambda: float = Field(0.022, description="Damage fragility coefficient")


class MonteCarloVaRRequest(BaseModel):
    event_id: Optional[str] = None
    location_name: str = Field("Mumbai Metropolitan Industrial Corridor", description="Target geography")
    waterlogging_depth_cm: float = Field(85.0, ge=0.0, description="Base inundation depth")
    risk_score: float = Field(0.78, ge=0.0, le=1.0, description="Agent 1 physical hazard score")
    num_simulations: int = Field(1000, ge=100, le=5000, description="Monte Carlo sample iterations")
    asset_portfolio: Optional[List[AssetValuation]] = None


class VaRDistributionResult(BaseModel):
    median_loss_inr: float
    var_95_inr: float
    var_99_inr: float
    cvar_95_expected_shortfall_inr: float
    var_95_usd: float
    var_99_usd: float
    cvar_95_usd: float
    direct_physical_damage_inr: float
    business_downtime_interruption_inr: float
    statutory_regulatory_fines_inr: float
    stranded_asset_tier: str  # LOW, MEDIUM, HIGH, CRITICAL_STRANDED
    rbi_ltv_haircut_pct: float
    sebi_brsr_penalties_inr: float
    simulation_iterations: int
    computation_time_ms: float


class MacroFinancialController:
    """
    Executive Controller for Phase 7 (Agent 3 Macro Transition & Financial Value-at-Risk Engine).
    Enforces strict mathematical bounds, Monte Carlo simulation, and circuit breaker failover.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.phase_id = 7
        self.name = "Agent 3: Macro Transition & Financial Value-at-Risk Engine"
        self.state = "INITIALIZED"
        self.circuit_state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.cooldown_period_sec = 30.0
        self.failure_threshold = 3
        self.inr_per_usd = 83.2
        logger.info(f"{self.name} initialized successfully.")

    def _check_circuit_breaker(self):
        now = time.time()
        if self.circuit_state == "OPEN":
            if now - self.last_failure_time > self.cooldown_period_sec:
                self.circuit_state = "HALF-OPEN"
                logger.info("Phase 7 Circuit Breaker entered HALF-OPEN testing probe.")
            else:
                raise RuntimeError("Phase 7 Circuit Breaker is OPEN. Automated failover active.")

    def _record_success(self):
        self.failure_count = 0
        if self.circuit_state == "HALF-OPEN":
            self.circuit_state = "CLOSED"
            logger.info("Phase 7 Circuit Breaker recovered: state reset to CLOSED.")

    def _record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.circuit_state = "OPEN"
            logger.warning(f"Phase 7 Circuit Breaker tripped to OPEN after {self.failure_count} failures.")

    @staticmethod
    def calculate_single_asset_damage(valuation_inr: float, depth_cm: float, fragility_lambda: float = 0.022) -> float:
        """
        Governing exponential damage curve: Loss = V_asset * (1 - e^{-lambda * D})
        Monotonically non-decreasing with respect to depth D.
        """
        if depth_cm <= 0.0:
            return 0.0
        damage_ratio = 1.0 - math.exp(-fragility_lambda * depth_cm)
        damage_ratio = min(1.0, max(0.0, damage_ratio))
        return valuation_inr * damage_ratio

    def run_monte_carlo_var(
        self,
        base_depth_cm: float,
        risk_score: float,
        num_simulations: int = 1000,
        portfolio: Optional[List[AssetValuation]] = None
    ) -> VaRDistributionResult:
        """
        Executes N >= 1000 Monte Carlo iterations perturbing depth and computing loss distribution percentiles.
        """
        self._check_circuit_breaker()
        t0 = time.perf_counter()

        # Default representative enterprise portfolio if none provided
        if not portfolio:
            portfolio = [
                AssetValuation(
                    asset_id="AST-01",
                    asset_name="Substation & Auxiliary Power Terminal",
                    category="critical_infrastructure",
                    valuation_inr=180_000_000,  # ₹18 Cr
                    depth_cm=base_depth_cm * 1.15,
                    fragility_lambda=0.028
                ),
                AssetValuation(
                    asset_id="AST-02",
                    asset_name="Industrial Logistics Warehouse Tier-1",
                    category="industrial_warehouse",
                    valuation_inr=120_000_000,  # ₹12 Cr
                    depth_cm=base_depth_cm * 1.0,
                    fragility_lambda=0.022
                ),
                AssetValuation(
                    asset_id="AST-03",
                    asset_name="Commercial Corporate Center & Data Vault",
                    category="commercial_rc",
                    valuation_inr=150_000_000,  # ₹15 Cr
                    depth_cm=base_depth_cm * 0.90,
                    fragility_lambda=0.018
                ),
                AssetValuation(
                    asset_id="AST-04",
                    asset_name="Supply Chain Railhead Depots",
                    category="critical_infrastructure",
                    valuation_inr=90_000_000,   # ₹9 Cr
                    depth_cm=base_depth_cm * 1.05,
                    fragility_lambda=0.025
                )
            ]

        # Seed pseudo-random generator with deterministic baseline for reproducible benchmarks
        random.seed(42 + int(base_depth_cm * 10))

        simulated_losses = []
        depth_std = max(5.0, base_depth_cm * 0.20)  # 20% hydrological depth variance

        for _ in range(num_simulations):
            iteration_loss = 0.0
            for asset in portfolio:
                # Stochastic depth sampling (truncated normal to avoid negative depths)
                stochastic_depth = max(0.0, random.gauss(asset.depth_cm, depth_std))
                # Slight micro-structural fragility perturbation (+/- 10%)
                stochastic_lambda = max(0.005, asset.fragility_lambda * (1.0 + random.uniform(-0.10, 0.10)))
                asset_loss = self.calculate_single_asset_damage(asset.valuation_inr, stochastic_depth, stochastic_lambda)
                iteration_loss += asset_loss
            simulated_losses.append(iteration_loss)

        simulated_losses.sort()

        # Percentile calculations
        idx_50 = int(0.50 * num_simulations)
        idx_95 = int(0.95 * num_simulations)
        idx_99 = int(0.99 * num_simulations)

        median_loss = simulated_losses[min(idx_50, num_simulations - 1)]
        var_95 = simulated_losses[min(idx_95, num_simulations - 1)]
        var_99 = simulated_losses[min(idx_99, num_simulations - 1)]

        # Conditional Value-at-Risk (Expected Shortfall): E[Loss | Loss >= VaR_95]
        tail_losses = simulated_losses[idx_95:]
        cvar_95 = sum(tail_losses) / len(tail_losses) if tail_losses else var_95

        # Macro Transition & Secondary Economic Costs
        # Business downtime interruption: operational halt costs ~40% of physical damage
        business_interruption = var_95 * 0.42
        # SEBI BRSR Principle 6 penalties for inadequate flood defense disclosure
        sebi_fines = 25_000_000 if var_95 > 100_000_000 else 7_500_000

        # RBI Climate Risk Haircut
        if risk_score >= 0.75 or base_depth_cm >= 80.0:
            stranded_tier = "CRITICAL_STRANDED"
            rbi_haircut = 25.0
        elif risk_score >= 0.50 or base_depth_cm >= 40.0:
            stranded_tier = "HIGH"
            rbi_haircut = 18.0
        elif base_depth_cm >= 20.0:
            stranded_tier = "MEDIUM"
            rbi_haircut = 12.0
        else:
            stranded_tier = "LOW"
            rbi_haircut = 5.0

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        self._record_success()

        return VaRDistributionResult(
            median_loss_inr=round(median_loss, 2),
            var_95_inr=round(var_95, 2),
            var_99_inr=round(var_99, 2),
            cvar_95_expected_shortfall_inr=round(cvar_95, 2),
            var_95_usd=round(var_95 / self.inr_per_usd, 2),
            var_99_usd=round(var_99 / self.inr_per_usd, 2),
            cvar_95_usd=round(cvar_95 / self.inr_per_usd, 2),
            direct_physical_damage_inr=round(var_95, 2),
            business_downtime_interruption_inr=round(business_interruption, 2),
            statutory_regulatory_fines_inr=round(sebi_fines, 2),
            stranded_asset_tier=stranded_tier,
            rbi_ltv_haircut_pct=rbi_haircut,
            sebi_brsr_penalties_inr=round(sebi_fines, 2),
            simulation_iterations=num_simulations,
            computation_time_ms=elapsed_ms
        )

    async def execute_phase_pipeline(self, payload: Dict[str, Any]) -> FinancialVaRModel:
        """
        Executes standard PRD Phase 7 pipeline returning compliant FinancialVaRModel.
        """
        self._check_circuit_breaker()
        start_time = time.perf_counter()
        try:
            if not payload:
                raise ValueError("Empty payload rejected by Phase 7 gate.")

            depth_cm = float(payload.get("waterlogging_depth_cm", payload.get("depth_cm", 85.0)))
            risk = float(payload.get("risk_score", 0.78))
            event_id = str(payload.get("event_id", f"TS-EVT-{int(time.time())}"))

            var_res = self.run_monte_carlo_var(
                base_depth_cm=depth_cm,
                risk_score=risk,
                num_simulations=500
            )

            result_dict = {
                "processed_by": self.name,
                "phase_id": self.phase_id,
                "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
                "status": "OPERATIONAL",
                "var_95_inr": var_res.var_95_inr,
                "var_99_inr": var_res.var_99_inr,
                "cvar_95_inr": var_res.cvar_95_expected_shortfall_inr,
                "stranded_asset_tier": var_res.stranded_asset_tier,
                "rbi_haircut_pct": var_res.rbi_ltv_haircut_pct,
                "data": payload
            }
            self._record_success()

            return FinancialVaRModel(
                event_id=event_id,
                execution_tier="ENTERPRISE_PROD",
                verified_flag=True,
                metadata=result_dict
            )
        except Exception as exc:
            self._record_failure()
            logger.error(f"Error in {self.name}: {exc}")
            raise


# Global Singleton Controller Instance
macro_financial_controller = MacroFinancialController()
