"""
Geospatial GeoJSON Layer Router
Generates and serves GIS boundary polygons, flood inundation layers, drainage canals, and building footprint overlays.
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException

from backend.app.agent2_geo import chronic_geo_engine

router = APIRouter(tags=["Geospatial Layers"])


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
