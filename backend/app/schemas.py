"""
Pydantic Schemas for AEGIS-CLIMATE
Defines strict data models for API requests, agent results, and WebSocket streams.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class AnalyzeRequest(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0, description="Latitude coordinate", example=19.0760)
    lon: float = Field(..., ge=-180.0, le=180.0, description="Longitude coordinate", example=72.8777)
    location_name: Optional[str] = Field(None, description="Human-readable location label", example="Mumbai Mithi River Basin")
    radius_km: float = Field(10.0, ge=1.0, le=100.0, description="Analysis radius in kilometers")
    
    # What-If Simulation Parameters (Winning Feature)
    simulated_additional_rain_mm: float = Field(0.0, ge=0.0, le=300.0, description="Simulated incremental rainfall")
    simulated_saturation_pct_override: Optional[float] = Field(None, ge=0.0, le=100.0, description="Override soil saturation percentage")


class RiskMetrics(BaseModel):
    precipitation_24h_mm: float = Field(..., description="Precipitation accumulated in last 24 hours")
    precipitation_7d_mm: float = Field(..., description="Antecedent 7-day rolling precipitation")
    soil_saturation_pct: float = Field(..., description="Soil moisture saturation index percentage")
    relative_humidity_pct: float = Field(..., description="Current relative humidity percentage")
    elevation_m: float = Field(..., description="Topographical elevation in meters above sea level")
    temperature_c: Optional[float] = Field(None, description="Ambient air temperature in Celsius")


class Agent1Result(BaseModel):
    status: str = Field("COMPLETED", description="Agent execution status")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Flash flood probability score 0.0 to 1.0")
    risk_tier: str = Field(..., description="LOW, MEDIUM, HIGH, or CRITICAL")
    dominant_factor: str = Field(..., description="Key driving risk factor e.g. soil_saturation or heavy_rainfall")
    metrics: RiskMetrics
    triggered_chronic: bool = Field(..., description="Whether downstream Agent 2 was automatically activated")
    execution_time_ms: float = Field(..., description="Inference time in milliseconds")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class HorizonCurves(BaseModel):
    yr10: float = Field(..., alias="10yr", description="10-year cumulative structural vulnerability index")
    yr20: float = Field(..., alias="20yr", description="20-year cumulative structural vulnerability index")
    yr30: float = Field(..., alias="30yr", description="30-year cumulative structural vulnerability index")

    class Config:
        populate_by_name = True


class Agent2Result(BaseModel):
    status: str = Field("COMPLETED", description="Agent execution status")
    exposure_tier: str = Field(..., description="SUPERFICIAL_WATERLOGGING or INFRASTRUCTURE_FAILURE")
    waterlogging_depth_cm: int = Field(..., description="Estimated flood water depth in centimeters")
    buildings_at_risk: int = Field(..., description="Count of critical structures inside the inundation boundary")
    drainage_overflow_pct: float = Field(..., description="Municipal stormwater drainage capacity exceeded percentage")
    damage_estimate_inr: int = Field(..., description="Estimated 10-year direct structural damage in INR")
    damage_estimate_usd: int = Field(..., description="Estimated 10-year direct structural damage in USD")
    geo_overlay_geojson: Optional[str] = Field(None, description="Endpoint or GeoJSON polygon url")
    horizon_curves: HorizonCurves
    execution_time_ms: float
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class Agent3Result(BaseModel):
    status: str = Field("COMPLETED", description="Agent execution status")
    var_estimate_usd: int = Field(..., description="Enterprise Value at Risk (VaR) in USD")
    var_estimate_inr: int = Field(..., description="Enterprise Value at Risk (VaR) in INR")
    stranded_asset_risk: str = Field(..., description="LOW, MEDIUM, or HIGH likelihood of asset stranding")
    applicable_regulations: List[str] = Field(default_factory=list, description="Relevant policies retrieved by RAG")
    compliance_gap_pct: int = Field(..., description="Percentage shortfall in ESG/carbon compliance")
    recommended_actions: List[str] = Field(default_factory=list, description="Actionable mitigation recommendations")
    bilingual_alert_hindi: Optional[str] = Field(None, description="Localized Hindi civic alert for responders")
    bilingual_alert_english: Optional[str] = Field(None, description="Localized English civic alert")
    execution_time_ms: float
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class AgentTraceStep(BaseModel):
    agent_id: str
    step_name: str
    action_type: str  # "THOUGHT", "TOOL_CALL", "OBSERVATION", "DECISION"
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class UnifiedRiskResponse(BaseModel):
    event_id: str
    location_name: str
    lat: float
    lon: float
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    agent1: Agent1Result
    agent2: Optional[Agent2Result] = None
    agent3: Optional[Agent3Result] = None
    thought_trace: List[AgentTraceStep] = Field(default_factory=list)


class HotspotModel(BaseModel):
    id: str
    name: str
    state: str
    lat: float
    lon: float
    risk_profile: str
    description: str
    typical_annual_loss_inr: str


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str
    environment: str
    services: Dict[str, str]
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
