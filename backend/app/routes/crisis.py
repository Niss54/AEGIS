"""
TERRA-SENTINEL: Ushahidi Citizen Crisis Crowdsourcing & Verification Router
Phase 29.2: Ushahidi Platform REST API Endpoints
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException, Path
from backend.app.ushahidi_crisis import (
    ushahidi_engine,
    CitizenIncident,
    CitizenIncidentCreate,
    IncidentCategory,
    IncidentStatus
)

logger = logging.getLogger("terra_sentinel.routes.crisis")

router = APIRouter(tags=["Ushahidi Citizen Crisis Crowdsourcing"])


@router.post("/crisis/incidents", response_model=CitizenIncident)
async def create_citizen_incident(data: CitizenIncidentCreate):
    """
    Submits a crowdsourced citizen crisis report or SOS alert across Web, SMS, or Mesh channels.
    Calculates baseline credibility and assigns initial severity tier.
    """
    try:
        return ushahidi_engine.create_incident(data)
    except Exception as e:
        logger.error(f"Error creating citizen incident: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Citizen incident creation error: {str(e)}")


@router.get("/crisis/incidents", response_model=List[CitizenIncident])
async def list_citizen_incidents(
    status: Optional[IncidentStatus] = Query(None, description="Filter by verification lifecycle status"),
    category: Optional[IncidentCategory] = Query(None, description="Filter by incident crisis category"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of incidents to return")
):
    """
    Returns live crisis incident feed with optional status and category filtering.
    """
    return ushahidi_engine.list_incidents(status=status, category=category, limit=limit)


@router.get("/crisis/incidents/{incident_id}", response_model=CitizenIncident)
async def get_citizen_incident_by_id(
    incident_id: str = Path(..., description="Unique incident identifier (e.g., INC-MUM-001)")
):
    """
    Retrieves full incident record including multi-sensor verification traces.
    """
    inc = ushahidi_engine.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return inc


@router.post("/crisis/verify/{incident_id}", response_model=CitizenIncident)
@router.post("/crisis/incidents/{incident_id}/verify", response_model=CitizenIncident)
async def verify_citizen_incident(
    incident_id: str = Path(..., description="Unique incident identifier to verify"),
    sar_backscatter_db: float = Query(-4.0, description="Simulated/live Sentinel-1 SAR decibel backscatter (<= -3.5 dB confirms flood)"),
    lora_depth_cm: Optional[float] = Query(None, description="Simulated/live ClusterDuck LoRa water depth in cm")
):
    """
    Executes multi-sensor reality corroboration against Sentinel-1 SAR and ClusterDuck LoRa depth gauges.
    Automatically transitions incident status to VERIFIED or ESCALATED upon satisfying C_post >= 0.75.
    """
    try:
        return ushahidi_engine.verify_incident(
            incident_id=incident_id,
            simulated_sar_backscatter_db=sar_backscatter_db,
            simulated_lora_depth_cm=lora_depth_cm
        )
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Error verifying incident {incident_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Verification failure: {str(e)}")


@router.post("/crisis/witness/{incident_id}", response_model=CitizenIncident)
async def add_incident_witness(
    incident_id: str = Path(..., description="Unique incident identifier")
):
    """
    Registers a corroborating witness report, boosting credibility score.
    """
    try:
        return ushahidi_engine.add_witness(incident_id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Error adding witness to {incident_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crisis/spec")
async def get_crisis_engine_specification():
    """
    Returns architectural specifications, credibility formula, and channel mapping for the Ushahidi engine.
    """
    return {
        "engine": "Ushahidi Platform v3/v5 Citizen Crowdsourcing Core",
        "credibility_formulation": "C_post = 0.20*S_trust + 0.25*min(1.0, N_witness/3) + 0.30*I(SAR <= -3.5dB) + 0.25*min(1.0, D_LoRa/50cm)",
        "verification_threshold": 0.75,
        "supported_channels": [
            "WEB_PORTAL", "SMS_SYNC", "TWILIO_VOICE_SMS", "EMAIL_GATEWAY", "RADIO_MESH_LORA"
        ],
        "categories": [
            "FLOOD_WATERLOGGING", "TRAPPED_CIVILIANS", "INFRASTRUCTURE_FAILURE", "MEDICAL_EMERGENCY", "SUPPLY_DEFICIT"
        ],
        "active_incidents_count": len(ushahidi_engine._incidents)
    }
