"""
Geospatial GeoJSON Layer Router & Geolocation Resolver
Generates and serves GIS boundary polygons, flood inundation layers, drainage canals, building footprint overlays,
and resolves GPS coordinates to nearest jurisdictional climate hotspots with automatic language mapping.
"""
import math
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.agent2_geo import chronic_geo_engine
from backend.app.routes.hotspots import GLOBAL_HOTSPOTS
from backend.app.bhasha.engine import bhasha_engine

router = APIRouter(tags=["Geospatial Layers"])


class DetectLocationRequest(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0, description="Latitude from GPS")
    lon: float = Field(..., ge=-180.0, le=180.0, description="Longitude from GPS")


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance between two coordinate pairs in kilometers."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2.0) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)


@router.get("/geo/layer/{event_id}")
async def get_geo_layer(
    event_id: str,
    lat: float = 19.0728,
    lon: float = 72.8797,
    depth_cm: int = 85,
    severity: str = "INFRASTRUCTURE_FAILURE"
) -> Dict[str, Any]:
    """
    Returns full GeoJSON FeatureCollection containing multi-tier flood inundation perimeter polygons,
    drainage outflow conduits, and exposed structural markers for Leaflet.js rendering.
    """
    return chronic_geo_engine.generate_geojson_layers(
        event_id=event_id,
        lat=lat,
        lon=lon,
        depth_cm=depth_cm,
        severity=severity
    )


@router.post("/geo/detect-location")
async def detect_location(req: DetectLocationRequest) -> Dict[str, Any]:
    """
    Reverse geocoding and nearest climate hotspot matching for 1-Click GPS detection.
    Snaps user coordinates to nearest jurisdictional basin and resolves regional language profile.
    """
    nearest = None
    min_dist = float("inf")
    for h in GLOBAL_HOTSPOTS:
        dist = haversine_km(req.lat, req.lon, h.lat, h.lon)
        if dist < min_dist:
            min_dist = dist
            nearest = h

    profile = bhasha_engine.resolve_language(
        location_label=nearest.name if nearest else "User GPS Location",
        lat=req.lat,
        lon=req.lon,
        jurisdiction=nearest.jurisdiction if nearest else None
    )

    return {
        "status": "success",
        "query_coordinates": {"lat": req.lat, "lon": req.lon},
        "nearest_hotspot": nearest.model_dump() if hasattr(nearest, "model_dump") else (nearest.dict() if nearest else None),
        "distance_km": min_dist if min_dist != float("inf") else 0.0,
        "language_profile": {
            "code": profile.code,
            "short_code": profile.short_code,
            "name": profile.name,
            "native_name": profile.native_name,
            "flag_emoji": profile.flag_emoji,
            "civil_defense_agency": profile.civil_defense_agency,
            "currency_symbol": profile.currency_symbol,
            "currency_code": profile.currency_code
        }
    }
