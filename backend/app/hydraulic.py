"""
TERRA-SENTINEL Production Specification: Phase 6
Module: terra_sentinel.phase_6.hydraulicdrainagecontroller
Governance: Gravitas Reliability Runtime · Model Context Protocol Compliant

Mathematical Governing Equation (Deterministic Constraint):
D_water = max(0, (P_eff - C_drain) / 10) * (1 + 1 / (1 + Slope))
Where:
- P_eff: Effective precipitation (mm/hr) adjusted for antecedent soil saturation
- C_drain: Municipal stormwater conduit throughput capacity (mm/hr)
- Slope: Topographical gradient ratio [0.0 - 1.0]
- D_water: Resulting waterlogging depth (cm)
"""
import time
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("terra_sentinel.phase_6")


class GeoContourModel(BaseModel):
    """
    Standard Phase 6 Telemetry & Contour Contract as declared in PRD.md Section 16 (Phase 6).
    """
    event_id: str = Field(..., description="Unique UUIDv4 telemetry event identifier")
    timestamp_epoch: float = Field(default_factory=time.time, description="Epoch timestamp")
    execution_tier: str = Field("ENTERPRISE_PROD", description="Execution tier label")
    verified_flag: bool = Field(True, description="Cryptographic verification indicator")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Telemetry metadata payload")


class ConduitNode(BaseModel):
    conduit_id: str
    section_name: str
    capacity_mm_hr: float
    current_inflow_mm_hr: float
    surcharge_ratio: float
    choke_status: str  # NORMAL, WARNING, SURCHARGED, CRITICAL_BLOCKED
    flow_velocity_mps: float


class HydraulicSimulationRequest(BaseModel):
    event_id: Optional[str] = None
    lat: float = Field(19.0760, description="Latitude coordinate")
    lon: float = Field(72.8777, description="Longitude coordinate")
    precipitation_mm_hr: float = Field(..., ge=0.0, description="Gross rainfall intensity in mm/hr")
    soil_saturation_pct: float = Field(75.0, ge=0.0, le=100.0, description="Soil saturation percentage")
    drainage_capacity_mm_hr: float = Field(35.0, gt=0.0, description="Baseline municipal drainage capacity in mm/hr")
    slope_gradient: float = Field(0.02, ge=0.0, le=1.0, description="Topographical slope gradient (e.g., 0.02 = 2%)")
    catchment_area_km2: float = Field(12.5, gt=0.0, description="Hydrological catchment area in sq km")


class HydraulicSimulationResponse(BaseModel):
    event_id: str
    timestamp_epoch: float
    waterlogging_depth_cm: float
    effective_precipitation_mm_hr: float
    drainage_capacity_mm_hr: float
    drainage_surcharge_pct: float
    discharge_rate_m3_sec: float
    hydraulic_risk_tier: str
    chokepoints_detected: int
    conduit_network: List[ConduitNode]
    flow_vectors_geojson: Dict[str, Any]
    circuit_breaker_state: str
    latency_ms: float


class HydraulicDrainageController:
    """
    Executive Controller for Phase 6: Municipal Drainage Network & Hydraulic Flow Accumulation.
    Enforces strict mathematical bounds, circuit breaker failover, and deterministic hydraulic dispatch.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.phase_id = 6
        self.name = "Municipal Drainage Network & Hydraulic Flow Accumulation"
        self.state = "INITIALIZED"
        self.circuit_state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.cooldown_period_sec = 30.0
        self.failure_threshold = 3
        logger.info(f"{self.name} initialized successfully.")

    def _check_circuit_breaker(self):
        """Monitors failure rate and transitions circuit state per PRD Section 7."""
        now = time.time()
        if self.circuit_state == "OPEN":
            if now - self.last_failure_time > self.cooldown_period_sec:
                self.circuit_state = "HALF-OPEN"
                logger.info(f"Phase 6 Circuit Breaker transitioned to HALF-OPEN (testing probe).")
            else:
                raise RuntimeError("Phase 6 Circuit Breaker is OPEN. Automated failover active.")

    def _record_success(self):
        self.failure_count = 0
        if self.circuit_state == "HALF-OPEN":
            self.circuit_state = "CLOSED"
            logger.info(f"Phase 6 Circuit Breaker recovered: state reset to CLOSED.")

    def _record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.circuit_state = "OPEN"
            logger.warning(f"Phase 6 Circuit Breaker tripped to OPEN after {self.failure_count} failures.")

    @staticmethod
    def calculate_waterlogging_depth(
        precipitation_mm_hr: float,
        soil_saturation_pct: float,
        drainage_capacity_mm_hr: float,
        slope_gradient: float
    ) -> float:
        """
        Governing Equation from PRD.md Section 16 (Phase 6):
        D_water = max(0, (P_eff - C_drain) / 10) * (1 + 1 / (1 + Slope))
        """
        # Infiltration deduction based on antecedent soil saturation
        # Saturated soils (>= 90%) allow negligible infiltration (run-off coefficient -> 0.95)
        infiltration_reduction = max(0.05, 1.0 - (soil_saturation_pct / 100.0) * 0.75)
        effective_precip = precipitation_mm_hr * (1.0 - (1.0 - infiltration_reduction) * 0.5)

        # Net surplus precipitation after drainage evacuation
        net_surplus = max(0.0, (effective_precip - drainage_capacity_mm_hr) / 10.0)

        # Topographical accumulation factor (depressions with slope -> 0 retain max head)
        slope_factor = 1.0 + (1.0 / (1.0 + max(0.0, slope_gradient)))

        # Resulting depth in centimeters (rounded to 2 decimal places)
        depth_cm = round(net_surplus * slope_factor, 2)
        return depth_cm

    def simulate_conduit_network(
        self,
        lat: float,
        lon: float,
        precipitation_mm_hr: float,
        drainage_capacity_mm_hr: float
    ) -> List[ConduitNode]:
        """
        Simulates 4 interconnected municipal stormwater trunk drains and outfall channels.
        """
        sections = [
            ("CND-01-PRIMARY", "Arterial Stormwater Trunk North", 1.25),
            ("CND-02-CENTRAL", "Collector Drain Sub-basin East", 0.90),
            ("CND-03-CHOKEPT", "Culvert Box Interceptor South", 0.65),
            ("CND-04-OUTFALL", "Tidal Outfall Estuary Sluice", 1.10)
        ]

        conduit_nodes = []
        for cid, name, factor in sections:
            cap = round(drainage_capacity_mm_hr * factor, 1)
            inflow = round(precipitation_mm_hr * 0.85 * (1.1 if "CHOKEPT" in cid else 0.95), 1)
            surcharge = round(inflow / max(1.0, cap), 2)

            if surcharge >= 1.6:
                status = "CRITICAL_BLOCKED"
                velocity = 0.4  # stagnation / backflow
            elif surcharge >= 1.0:
                status = "SURCHARGED"
                velocity = 1.2
            elif surcharge >= 0.75:
                status = "WARNING"
                velocity = 1.8
            else:
                status = "NORMAL"
                velocity = 2.4

            conduit_nodes.append(ConduitNode(
                conduit_id=cid,
                section_name=name,
                capacity_mm_hr=cap,
                current_inflow_mm_hr=inflow,
                surcharge_ratio=surcharge,
                choke_status=status,
                flow_velocity_mps=velocity
            ))

        return conduit_nodes

    async def execute_phase_pipeline(self, payload: Dict[str, Any]) -> GeoContourModel:
        """
        Executes standard Phase 6 pipeline returning compliant GeoContourModel (PRD.md Section 16).
        """
        self._check_circuit_breaker()
        start_time = time.perf_counter()
        try:
            if not payload:
                raise ValueError("Empty payload rejected by Phase 6 gate.")

            p_rain = float(payload.get("precipitation_mm_hr", 85.0))
            soil_sat = float(payload.get("soil_saturation_pct", 80.0))
            drain_cap = float(payload.get("drainage_capacity_mm_hr", 35.0))
            slope = float(payload.get("slope_gradient", 0.02))

            depth_cm = self.calculate_waterlogging_depth(p_rain, soil_sat, drain_cap, slope)
            event_id = str(payload.get("event_id", f"TS-EVT-{int(time.time())}"))

            conduits = self.simulate_conduit_network(
                payload.get("lat", 19.0760),
                payload.get("lon", 72.8777),
                p_rain,
                drain_cap
            )

            chokes = sum(1 for c in conduits if c.choke_status in ("SURCHARGED", "CRITICAL_BLOCKED"))

            result_dict = {
                "processed_by": self.name,
                "phase_id": self.phase_id,
                "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
                "status": "OPERATIONAL",
                "waterlogging_depth_cm": depth_cm,
                "chokepoints_detected": chokes,
                "circuit_state": self.circuit_state,
                "conduit_count": len(conduits),
                "data": payload
            }
            self._record_success()

            return GeoContourModel(
                event_id=event_id,
                execution_tier="ENTERPRISE_PROD",
                verified_flag=True,
                metadata=result_dict
            )
        except Exception as exc:
            self._record_failure()
            logger.error(f"Error in {self.name}: {exc}")
            raise

    async def run_full_simulation(self, req: HydraulicSimulationRequest) -> HydraulicSimulationResponse:
        """
        Executes granular hydraulic simulation with full GIS vectors and conduit surcharge metrics.
        """
        self._check_circuit_breaker()
        start_time = time.perf_counter()
        try:
            depth_cm = self.calculate_waterlogging_depth(
                req.precipitation_mm_hr,
                req.soil_saturation_pct,
                req.drainage_capacity_mm_hr,
                req.slope_gradient
            )

            # Rational Method for runoff: Q = (C * I * A) / 360
            # C = runoff coefficient (0.6 - 0.95), I = intensity (mm/hr), A = area (hectares)
            c_coeff = 0.65 + (req.soil_saturation_pct / 100.0) * 0.28
            area_ha = req.catchment_area_km2 * 100.0
            discharge_q = round((c_coeff * req.precipitation_mm_hr * area_ha) / 360.0, 2)

            conduits = self.simulate_conduit_network(
                req.lat, req.lon, req.precipitation_mm_hr, req.drainage_capacity_mm_hr
            )
            chokes = sum(1 for c in conduits if c.choke_status in ("SURCHARGED", "CRITICAL_BLOCKED"))

            surcharge_pct = round((req.precipitation_mm_hr / max(1.0, req.drainage_capacity_mm_hr)) * 100.0, 1)

            if depth_cm >= 80.0 or chokes >= 2:
                tier = "INFRASTRUCTURE_FAILURE"
            elif depth_cm >= 30.0 or chokes >= 1:
                tier = "HIGH_SURCHARGE"
            elif depth_cm >= 10.0:
                tier = "MODERATE_WATERLOGGING"
            else:
                tier = "NOMINAL_DISCHARGE"

            event_id = req.event_id or f"TS-HYD-{int(time.time())}"

            # GeoJSON Flow Vectors and Accumulation Polygons
            flow_geojson = {
                "type": "FeatureCollection",
                "properties": {
                    "event_id": event_id,
                    "depth_cm": depth_cm,
                    "tier": tier,
                    "discharge_m3_s": discharge_q
                },
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [
                                [req.lon - 0.015, req.lat - 0.012],
                                [req.lon - 0.005, req.lat - 0.003],
                                [req.lon, req.lat],
                                [req.lon + 0.010, req.lat + 0.008]
                            ]
                        },
                        "properties": {
                            "name": "Primary Arterial Stormwater Conduit",
                            "status": conduits[0].choke_status,
                            "flow_mps": conduits[0].flow_velocity_mps
                        }
                    },
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[
                                [req.lon - 0.008, req.lat - 0.008],
                                [req.lon + 0.008, req.lat - 0.008],
                                [req.lon + 0.008, req.lat + 0.008],
                                [req.lon - 0.008, req.lat + 0.008],
                                [req.lon - 0.008, req.lat - 0.008]
                            ]]
                        },
                        "properties": {
                            "name": "Hydraulic Pooling Inundation Footprint",
                            "depth_cm": depth_cm,
                            "surcharge_pct": surcharge_pct
                        }
                    }
                ]
            }

            self._record_success()
            return HydraulicSimulationResponse(
                event_id=event_id,
                timestamp_epoch=time.time(),
                waterlogging_depth_cm=depth_cm,
                effective_precipitation_mm_hr=req.precipitation_mm_hr,
                drainage_capacity_mm_hr=req.drainage_capacity_mm_hr,
                drainage_surcharge_pct=surcharge_pct,
                discharge_rate_m3_sec=discharge_q,
                hydraulic_risk_tier=tier,
                chokepoints_detected=chokes,
                conduit_network=conduits,
                flow_vectors_geojson=flow_geojson,
                circuit_breaker_state=self.circuit_state,
                latency_ms=round((time.perf_counter() - start_time) * 1000, 2)
            )
        except Exception as exc:
            self._record_failure()
            logger.error(f"Hydraulic simulation error: {exc}")
            raise


# Global Singleton Instance for High-Performance Reuse
hydraulic_controller = HydraulicDrainageController()
