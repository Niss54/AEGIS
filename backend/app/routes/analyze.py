"""
Primary Analyze Route & Multi-Agent Orchestrator
Coordinates Agent 1, Agent 2, and Agent 3 execution cycle.
"""
import uuid
import time
import math
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
import httpx

from backend.app.schemas import (
    AnalyzeRequest, UnifiedRiskResponse, Agent1Result, Agent2Result, Agent3Result,
    RiskMetrics, HorizonCurves, AgentTraceStep
)
from backend.app.websocket import manager
from backend.app.agent1_ml import flood_ml_engine
from backend.app.agent2_geo import chronic_geo_engine
from backend.app.agent3_financial import financial_risk_engine

router = APIRouter(tags=["Analysis & Agent Orchestration"])

# In-memory store for events in Phase 1
HISTORICAL_EVENTS: Dict[str, UnifiedRiskResponse] = {}


class ToolPredictInput(BaseModel):
    soil_saturation_pct: float = Field(..., ge=0.0, le=100.0, example=85.0)
    precipitation_24h_mm: float = Field(..., ge=0.0, example=95.0)
    precipitation_7d_mm: float = Field(..., ge=0.0, example=240.0)
    relative_humidity_pct: float = Field(..., ge=0.0, le=100.0, example=88.0)
    elevation_m: float = Field(..., example=12.0)
    drainage_capacity_index: float = Field(65.0, ge=0.0, le=100.0, example=55.0)


class ToolGeoInput(BaseModel):
    lat: float = Field(..., example=19.0728)
    lon: float = Field(..., example=72.8797)
    risk_score: float = Field(..., ge=0.0, le=1.0, example=0.85)
    precipitation_24h_mm: float = Field(..., example=95.0)
    soil_saturation_pct: float = Field(..., example=88.0)
    elevation_m: float = Field(..., example=12.0)
    radius_km: float = Field(10.0, example=10.0)


@router.post("/tools/predict")
async def tool_predict_flood_risk(input_data: ToolPredictInput):
    """
    Dedicated ML Tool Endpoint for Agent 1.
    Evaluates meteorological feature matrix using trained GradientBoostingClassifier.
    Used by MCP Hub and external microservices.
    """
    prediction = flood_ml_engine.predict(
        soil_saturation_pct=input_data.soil_saturation_pct,
        precipitation_24h_mm=input_data.precipitation_24h_mm,
        precipitation_7d_mm=input_data.precipitation_7d_mm,
        relative_humidity_pct=input_data.relative_humidity_pct,
        elevation_m=input_data.elevation_m,
        drainage_capacity_index=input_data.drainage_capacity_index
    )
    return {
        "status": "success",
        "tool": "run_flood_classifier",
        **prediction
    }


@router.post("/tools/geo-exposure")
async def tool_compute_geo_exposure(input_data: ToolGeoInput):
    """
    Dedicated Geospatial Tool Endpoint for Agent 2.
    Computes 30m DEM elevation deltas, municipal drainage overflow, and HAZUS depth-damage estimates.
    Used by MCP Hub and external microservices.
    """
    res = chronic_geo_engine.analyze_structural_exposure(
        lat=input_data.lat,
        lon=input_data.lon,
        risk_score=input_data.risk_score,
        precipitation_24h_mm=input_data.precipitation_24h_mm,
        soil_saturation_pct=input_data.soil_saturation_pct,
        elevation_m=input_data.elevation_m,
        radius_km=input_data.radius_km
    )
    return {
        "status": "success",
        "tool": "compute_dem_exposure",
        **res
    }


class ToolVarInput(BaseModel):
    location_name: str = Field("Industrial Asset", example="Mumbai Logistics Hub")
    risk_score: float = Field(..., ge=0.0, le=1.0, example=0.85)
    waterlogging_depth_cm: int = Field(..., example=85)
    buildings_at_risk: int = Field(..., example=340)
    damage_estimate_inr: int = Field(..., example=250000000)
    sector: str = Field("Industrial & Enterprise", example="Industrial & Logistics")


@router.post("/tools/var-model")
async def tool_compute_financial_var(input_data: ToolVarInput):
    """
    Dedicated Financial VaR Tool Endpoint for Agent 3.
    Computes direct physical loss, downtime loss, regulatory penalties, and insurance surges.
    Used by MCP Hub and external microservices.
    """
    res = financial_risk_engine.model_financial_var(
        location_label=input_data.location_name,
        risk_score=input_data.risk_score,
        waterlogging_depth_cm=input_data.waterlogging_depth_cm,
        buildings_at_risk=input_data.buildings_at_risk,
        damage_estimate_inr=input_data.damage_estimate_inr,
        sector=input_data.sector
    )
    return {
        "status": "success",
        "tool": "model_var_exposure",
        **res
    }


@router.post("/tools/policy-rag")
async def tool_query_policy_rag(query: str, top_k: int = 3):
    """Queries ChromaDB regulatory vector collection for matching climate policy clauses."""
    clauses = financial_risk_engine.rag.query(query, top_k=top_k)
    return {
        "status": "success",
        "tool": "query_policy_rag",
        "query": query,
        "results_count": len(clauses),
        "clauses": clauses
    }


@router.get("/tools/model-info")
async def get_model_info():
    """Returns training parameters, cross-validation metrics, and feature importance rankings."""
    return {
        "is_trained": flood_ml_engine.is_trained(),
        "metadata": flood_ml_engine.metadata
    }



async def fetch_open_meteo_telemetry(lat: float, lon: float) -> Dict[str, float]:
    """Fetch live meteorological vectors from Open-Meteo API with graceful fallback."""
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&hourly=precipitation,relative_humidity_2m,soil_moisture_0_to_1cm"
        f"&current=temperature_2m,relative_humidity_2m,precipitation&timezone=auto"
    )
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                current = data.get("current", {})
                hourly = data.get("hourly", {})
                
                precip_hourly = hourly.get("precipitation", [0.0] * 24)
                precip_24h = sum(precip_hourly[-24:]) if len(precip_hourly) >= 24 else sum(precip_hourly)
                
                soil_hourly = hourly.get("soil_moisture_0_to_1cm", [0.35])
                latest_soil = (soil_hourly[-1] if soil_hourly else 0.35) * 100  # convert m³/m³ to approx pct
                
                return {
                    "precipitation_24h_mm": round(precip_24h, 2),
                    "precipitation_7d_mm": round(precip_24h * 2.8, 2),
                    "soil_saturation_pct": round(min(100.0, max(20.0, latest_soil * 2.2)), 1),
                    "relative_humidity_pct": round(float(current.get("relative_humidity_2m", 78.0)), 1),
                    "temperature_c": round(float(current.get("temperature_2m", 28.5)), 1),
                    "elevation_m": round(float(data.get("elevation", 14.0)), 1)
                }
    except Exception as e:
        # Fallback based on coordinate geographic characteristics
        pass

    # Deterministic natural fallback if external API is rate-limited or offline
    base_precip = 65.0 if (18.5 <= lat <= 20.0 and 72.5 <= lon <= 73.5) else 35.0  # Higher for Mumbai
    return {
        "precipitation_24h_mm": base_precip,
        "precipitation_7d_mm": base_precip * 2.4,
        "soil_saturation_pct": 82.5 if base_precip > 50 else 48.0,
        "relative_humidity_pct": 85.0,
        "temperature_c": 29.0,
        "elevation_m": 12.0
    }


def compute_acute_risk(telemetry: Dict[str, float], sim_rain: float = 0.0, sim_sat: Optional[float] = None) -> (float, str, str, RiskMetrics, Dict[str, Any]):
    """
    Computes flood probability score [0.0 - 1.0] and risk tier using the trained ML model.
    Incorporates 'What-If' simulation adjustments.
    """
    precip_24h = telemetry["precipitation_24h_mm"] + sim_rain
    precip_7d = telemetry["precipitation_7d_mm"] + (sim_rain * 1.5)
    soil_sat = sim_sat if sim_sat is not None else telemetry["soil_saturation_pct"]
    humidity = telemetry["relative_humidity_pct"]
    elevation = telemetry["elevation_m"]

    # Run trained Gradient Boosting Classifier
    pred = flood_ml_engine.predict(
        soil_saturation_pct=soil_sat,
        precipitation_24h_mm=precip_24h,
        precipitation_7d_mm=precip_7d,
        relative_humidity_pct=humidity,
        elevation_m=elevation,
        drainage_capacity_index=65.0
    )

    score = pred["risk_score"]
    tier = pred["risk_tier"]
    dominant = pred["dominant_factor"]

    metrics = RiskMetrics(
        precipitation_24h_mm=round(precip_24h, 2),
        precipitation_7d_mm=round(precip_7d, 2),
        soil_saturation_pct=round(soil_sat, 1),
        relative_humidity_pct=round(humidity, 1),
        elevation_m=round(elevation, 1),
        temperature_c=telemetry.get("temperature_c", 28.0)
    )
    return score, tier, dominant, metrics, pred


@router.post("/analyze", response_model=UnifiedRiskResponse)
async def analyze_location(req: AnalyzeRequest):
    """
    Execute full multi-agent climate risk analysis for target coordinate.
    Runs Agent 1, and conditionally cascades to Agent 2 and Agent 3.
    """
    event_id = f"evt-{uuid.uuid4().hex[:8]}"
    location_label = req.location_name or f"Zone ({req.lat:.4f}°N, {req.lon:.4f}°E)"
    start_all = time.time()
    thought_trace: List[AgentTraceStep] = []

    # ----------------------------------------------------
    # AGENT 1: ACUTE PHYSICAL RISK AGENT
    # ----------------------------------------------------
    thought_trace.append(AgentTraceStep(
        agent_id="agent-1-acute",
        step_name="Ingest Telemetry",
        action_type="THOUGHT",
        content=f"Activating Acute Physical Risk Agent for {location_label}. Querying Open-Meteo environmental telemetry."
    ))

    # Broadcast live step via WebSocket
    await manager.broadcast_step(
        agent_id="agent-1-acute",
        step_name="Ingest Telemetry",
        action_type="TOOL_CALL",
        content=f"Fetching meteorological vectors for lat={req.lat}, lon={req.lon}"
    )

    t0 = time.time()
    telemetry = await fetch_open_meteo_telemetry(req.lat, req.lon)
    risk_score, risk_tier, dominant, metrics, pred = compute_acute_risk(
        telemetry,
        sim_rain=req.simulated_additional_rain_mm,
        sim_sat=req.simulated_saturation_pct_override
    )
    t1 = time.time()

    triggered_chronic = risk_score > 0.65

    probs_summary = ", ".join([f"{k}: {v*100:.1f}%" for k, v in pred.get("probabilities", {}).items()])
    thought_trace.append(AgentTraceStep(
        agent_id="agent-1-acute",
        step_name="ML Classification (GradientBoosting)",
        action_type="OBSERVATION",
        content=f"Telemetry: 24h Rain={metrics.precipitation_24h_mm}mm, Soil Saturation={metrics.soil_saturation_pct}%. Model: {pred.get('engine')}. Risk Score={risk_score} ({risk_tier}). Dominant factor: {dominant}. Probabilities: [{probs_summary}]."
    ))

    thought_trace.append(AgentTraceStep(
        agent_id="agent-1-acute",
        step_name="Threshold Evaluation",
        action_type="DECISION",
        content=f"Risk Score {risk_score} {'EXCEEDS' if triggered_chronic else 'DOES NOT EXCEED'} trigger threshold 0.65. {'Auto-triggering Chronic Vulnerability Agent (Agent 2).' if triggered_chronic else 'Pipeline complete.'}"
    ))

    agent1_res = Agent1Result(
        status="COMPLETED",
        risk_score=risk_score,
        risk_tier=risk_tier,
        dominant_factor=dominant,
        metrics=metrics,
        triggered_chronic=triggered_chronic,
        execution_time_ms=round((t1 - t0) * 1000, 2)
    )

    # ----------------------------------------------------
    # AGENT 2: CHRONIC CLIMATE VULNERABILITY AGENT (Conditional)
    # ----------------------------------------------------
    agent2_res: Optional[Agent2Result] = None
    if triggered_chronic:
        thought_trace.append(AgentTraceStep(
            agent_id="agent-2-chronic",
            step_name="Load Topography & DEM",
            action_type="THOUGHT",
            content="Received risk alert from Agent 1. Initiating 30m SRTM DEM topographical overlay and civic drainage capacity analysis."
        ))

        await manager.broadcast_step(
            agent_id="agent-2-chronic",
            step_name="Geospatial Ingestion",
            action_type="TOOL_CALL",
            content="Intersecting flood boundary with municipal drainage polygons and building footprints."
        )

        t_geo_0 = time.time()
        geo_result = chronic_geo_engine.analyze_structural_exposure(
            lat=req.lat,
            lon=req.lon,
            risk_score=risk_score,
            precipitation_24h_mm=metrics.precipitation_24h_mm,
            soil_saturation_pct=metrics.soil_saturation_pct,
            elevation_m=metrics.elevation_m,
            radius_km=req.radius_km
        )
        waterlogging_depth = geo_result["waterlogging_depth_cm"]
        drainage_overflow = geo_result["drainage_overflow_pct"]
        buildings_count = geo_result["buildings_at_risk"]
        damage_usd = geo_result["damage_estimate_usd"]
        damage_inr = geo_result["damage_estimate_inr"]
        exposure_tier = geo_result["exposure_tier"]

        thought_trace.append(AgentTraceStep(
            agent_id="agent-2-chronic",
            step_name="HAZUS Structural Loss Estimation",
            action_type="OBSERVATION",
            content=f"Computed waterlogging depth: {waterlogging_depth} cm. Municipal drainage over capacity by {drainage_overflow}%. {buildings_count} critical structures in hazard zone. Estimated structural damage: ₹{damage_inr / 10000000:.2f} Crores ($ {damage_usd / 1000000:.2f}M)."
        ))

        agent2_res = Agent2Result(
            status="COMPLETED",
            exposure_tier=exposure_tier,
            waterlogging_depth_cm=waterlogging_depth,
            buildings_at_risk=buildings_count,
            drainage_overflow_pct=drainage_overflow,
            damage_estimate_inr=damage_inr,
            damage_estimate_usd=damage_usd,
            geo_overlay_geojson=f"/api/v1/geo/layer/{event_id}",
            horizon_curves=HorizonCurves(**geo_result["horizon_curves"]),
            execution_time_ms=geo_result["execution_time_ms"]
        )

    # ----------------------------------------------------
    # AGENT 3: MACRO TRANSITION & FINANCIAL RISK AGENT (Conditional)
    # Triggered whenever Agent 2 identifies high/critical infrastructure exposure
    # ----------------------------------------------------
    agent3_res: Optional[Agent3Result] = None
    if agent2_res and (agent2_res.exposure_tier == "INFRASTRUCTURE_FAILURE" or risk_tier in ["HIGH", "CRITICAL"]):
        thought_trace.append(AgentTraceStep(
            agent_id="agent-3-financial",
            step_name="Policy Corpus RAG Retrieval",
            action_type="THOUGHT",
            content=f"Structural hazard detected by Agent 2 (depth={agent2_res.waterlogging_depth_cm}cm, {agent2_res.buildings_at_risk} buildings at risk). Querying ChromaDB vector store for applicable SEBI BRSR and carbon penalty mandates."
        ))

        await manager.broadcast_step(
            agent_id="agent-3-financial",
            step_name="Regulatory Retrieval",
            action_type="TOOL_CALL",
            content="Vector similarity search across BRSR Core, NDMA urban standards, and carbon tax schemas."
        )

        t_fin_0 = time.time()
        fin_result = financial_risk_engine.model_financial_var(
            location_label=location_label,
            risk_score=risk_score,
            waterlogging_depth_cm=agent2_res.waterlogging_depth_cm,
            buildings_at_risk=agent2_res.buildings_at_risk,
            damage_estimate_inr=agent2_res.damage_estimate_inr,
            sector="Industrial & Logistics Infrastructure"
        )

        var_usd = fin_result["var_estimate_usd"]
        var_inr = fin_result["var_estimate_inr"]
        stranded_risk = fin_result["stranded_asset_risk"]
        compliance_gap_pct = fin_result["compliance_gap_pct"]
        applicable_regulations = fin_result["applicable_regulations"]
        recommended_actions = fin_result["recommended_actions"]
        hindi_alert = fin_result["bilingual_alert_hindi"]
        english_alert = fin_result["bilingual_alert_english"]

        thought_trace.append(AgentTraceStep(
            agent_id="agent-3-financial",
            step_name="Value-at-Risk Synthesis & RAG Alignment",
            action_type="DECISION",
            content=f"Synthesized corporate VaR: ₹{var_inr / 10000000:.2f} Crores ($ {var_usd / 1000000:.2f}M). Stranded asset risk: {stranded_risk}. Compliance Gap: {compliance_gap_pct}%. Ingested {len(applicable_regulations)} policy mandates via ChromaDB."
        ))

        agent3_res = Agent3Result(
            status="COMPLETED",
            var_estimate_usd=var_usd,
            var_estimate_inr=var_inr,
            stranded_asset_risk=stranded_risk,
            applicable_regulations=applicable_regulations,
            compliance_gap_pct=compliance_gap_pct,
            recommended_actions=recommended_actions,
            bilingual_alert_hindi=hindi_alert,
            bilingual_alert_english=english_alert,
            execution_time_ms=fin_result["execution_time_ms"]
        )

    response = UnifiedRiskResponse(
        event_id=event_id,
        location_name=location_label,
        lat=req.lat,
        lon=req.lon,
        agent1=agent1_res,
        agent2=agent2_res,
        agent3=agent3_res,
        thought_trace=thought_trace
    )

    HISTORICAL_EVENTS[event_id] = response
    return response


@router.get("/events", response_model=List[UnifiedRiskResponse])
async def list_events():
    """Retrieve historical risk events analyzed during session."""
    return list(HISTORICAL_EVENTS.values())


@router.get("/events/{event_id}", response_model=UnifiedRiskResponse)
async def get_event(event_id: str):
    """Retrieve detailed multi-agent report for a single event."""
    if event_id not in HISTORICAL_EVENTS:
        raise HTTPException(status_code=404, detail="Event not found")
    return HISTORICAL_EVENTS[event_id]


@router.get("/events/{event_id}/structural", response_model=Agent2Result)
async def get_event_structural(event_id: str):
    """Retrieve Agent 2 structural exposure report for a specific event."""
    if event_id not in HISTORICAL_EVENTS:
        raise HTTPException(status_code=404, detail="Event not found")
    event = HISTORICAL_EVENTS[event_id]
    if not event.agent2:
        raise HTTPException(status_code=404, detail="Structural analysis was not triggered for this low-risk event")
    return event.agent2


@router.get("/events/{event_id}/financial", response_model=Agent3Result)
async def get_event_financial(event_id: str):
    """Retrieve Agent 3 Value at Risk and regulatory compliance report for a specific event."""
    if event_id not in HISTORICAL_EVENTS:
        raise HTTPException(status_code=404, detail="Event not found")
    event = HISTORICAL_EVENTS[event_id]
    if not event.agent3:
        raise HTTPException(status_code=404, detail="Financial VaR modeling was not triggered for this event")
    return event.agent3


