"""
AEGIS-CLIMATE: Evacuation Routing & Fleet Dispatch REST API Router
Phase 28: Mission-Critical Municipal Disaster Navigation Endpoints
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from backend.app.evacuation_routing import (
    evacuation_engine,
    VehicleType,
    EvacuationRouteRequest,
    EvacuationRouteResponse,
    FleetDispatchResponse,
    FleetUnit
)

logger = logging.getLogger("aegis.routes.evacuation")

router = APIRouter(tags=["Disaster Evacuation & Rescue Fleet"])


@router.post("/evacuation/routes", response_model=EvacuationRouteResponse)
async def compute_safe_evacuation_route(req: EvacuationRouteRequest):
    """
    Computes an optimal, water-depth constrained disaster evacuation corridor.
    Dynamically routes around submerged underpasses and lowlands based on vehicle clearance.
    """
    return evacuation_engine.compute_safe_evacuation_route(req)


@router.get("/evacuation/routes", response_model=EvacuationRouteResponse)
async def get_safe_evacuation_route_get(
    vehicle_type: VehicleType = Query(VehicleType.EMERGENCY_AMBULANCE, description="Transport vehicle type"),
    civilians_count: int = Query(25, ge=1, le=500, description="Civilian headcount")
):
    """
    GET query variant for fast pre-flight evacuation route computation.
    """
    req = EvacuationRouteRequest(
        origin_name="Kurla West Lowland Cluster",
        origin_lat=19.0685,
        origin_lon=72.8792,
        vehicle_type=vehicle_type,
        civilians_count=civilians_count
    )
    return evacuation_engine.compute_safe_evacuation_route(req)


@router.post("/evacuation/fleet-dispatch", response_model=FleetDispatchResponse)
async def dispatch_emergency_rescue_fleet(
    target_sector: str = Query("Kurla West Lowlands", description="Disaster sector name")
):
    """
    Mobilizes NDRF Inflatable Rescue Boats (IRB) and BMC high-clearance buses
    to extract trapped civilians from isolated flood clusters.
    """
    return evacuation_engine.dispatch_rescue_fleet(target_sector)


@router.get("/evacuation/fleet", response_model=List[FleetUnit])
async def get_rescue_fleet_units():
    """
    Retrieves real-time telemetry, location coordinates, fuel/battery %,
    and assignment status for all active municipal and NDRF rescue fleet units.
    """
    return evacuation_engine.get_fleet_status()


@router.get("/evacuation/health")
async def get_evacuation_health():
    """Lightweight health probe for evacuation routing engine."""
    return {
        "status": "operational",
        "service": "Disaster Evacuation Routing & Fleet Dispatch",
        "circuit_state": evacuation_engine.circuit_state
    }
