"""
Geospatial GeoJSON Layer Router
Generates and serves GIS boundary polygons, flood inundation layers, and building footprint overlays.
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
import math

router = APIRouter(tags=["Geospatial Layers"])


@router.get("/geo/layer/{event_id}")
async def get_geo_layer(event_id: str, lat: float = 19.0728, lon: float = 72.8797, depth_cm: int = 85) -> Dict[str, Any]:
    """
    Returns GeoJSON FeatureCollection containing flood inundation perimeter polygons
    and exposed structural markers for Leaflet.js rendering.
    """
    # Generate realistic inundation polygon around center coordinate
    points = 16
    radius_deg = 0.015  # Approx 1.6 km radius
    coordinates = []
    
    for i in range(points + 1):
        angle = (i / points) * 2 * math.pi
        # Introduce natural topographical jitter
        jitter = 1.0 + 0.18 * math.sin(3 * angle) + 0.12 * math.cos(5 * angle)
        pt_lat = lat + (radius_deg * jitter * math.cos(angle))
        pt_lon = lon + (radius_deg * 1.15 * jitter * math.sin(angle))
        coordinates.append([round(pt_lon, 5), round(pt_lat, 5)])

    # Sample exposed buildings
    building_markers = [
        {"name": "Substation Alpha-1", "type": "critical_power", "offset": (0.003, 0.004), "depth_cm": depth_cm + 10},
        {"name": "Municipal Water Pumping Station", "type": "water_infra", "offset": (-0.004, 0.002), "depth_cm": depth_cm + 25},
        {"name": "Metro Transit Line 3 Pier", "type": "transit", "offset": (0.005, -0.006), "depth_cm": depth_cm - 15},
        {"name": "Commercial Logistics Depot", "type": "commercial", "offset": (-0.006, -0.005), "depth_cm": depth_cm + 5},
    ]

    features = [
        {
            "type": "Feature",
            "properties": {
                "layer_type": "inundation_zone",
                "waterlogging_depth_cm": depth_cm,
                "severity": "CRITICAL" if depth_cm > 75 else "HIGH",
                "fill_color": "#D62828" if depth_cm > 75 else "#E76F51",
                "fill_opacity": 0.45
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [coordinates]
            }
        }
    ]

    for b in building_markers:
        features.append({
            "type": "Feature",
            "properties": {
                "layer_type": "exposed_building",
                "name": b["name"],
                "category": b["type"],
                "local_depth_cm": b["depth_cm"],
                "risk_status": "VULNERABLE"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [round(lon + b["offset"][1], 5), round(lat + b["offset"][0], 5)]
            }
        })

    return {
        "type": "FeatureCollection",
        "metadata": {
            "event_id": event_id,
            "center": [lat, lon],
            "projected_crs": "EPSG:4326"
        },
        "features": features
    }
