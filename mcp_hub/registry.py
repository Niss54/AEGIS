"""
MCP Hub Tool Registry
Catalogs tools with JSON-RPC compliant schemas for dynamic agent discovery.
"""
from typing import Dict, Any

TOOLS_REGISTRY: Dict[str, Dict[str, Any]] = {
    "fetch_weather_vectors": {
        "name": "fetch_weather_vectors",
        "description": "Fetches near-real-time environmental telemetry (hourly precipitation, antecedent rain, soil moisture, humidity) from Open-Meteo API.",
        "parameters": {
            "type": "object",
            "properties": {
                "lat": {"type": "number", "description": "Latitude coordinate"},
                "lon": {"type": "number", "description": "Longitude coordinate"}
            },
            "required": ["lat", "lon"]
        },
        "target_agent": "agent-1-acute"
    },
    "run_flood_classifier": {
        "name": "run_flood_classifier",
        "description": "Applies locally trained XGBoost model against feature matrix to compute localized flash flood probability score [0.0 - 1.0].",
        "parameters": {
            "type": "object",
            "properties": {
                "precipitation_24h_mm": {"type": "number"},
                "precipitation_7d_mm": {"type": "number"},
                "soil_saturation_pct": {"type": "number"},
                "relative_humidity_pct": {"type": "number"},
                "elevation_m": {"type": "number"}
            },
            "required": ["precipitation_24h_mm", "precipitation_7d_mm", "soil_saturation_pct", "relative_humidity_pct", "elevation_m"]
        },
        "target_agent": "agent-1-acute"
    },
    "compute_dem_exposure": {
        "name": "compute_dem_exposure",
        "description": "Analyzes 30m SRTM Digital Elevation Model, municipal drainage capacity logs, and building polygons to classify infrastructure failure risk.",
        "parameters": {
            "type": "object",
            "properties": {
                "lat": {"type": "number"},
                "lon": {"type": "number"},
                "risk_score": {"type": "number"},
                "radius_km": {"type": "number", "default": 10.0}
            },
            "required": ["lat", "lon", "risk_score"]
        },
        "target_agent": "agent-2-chronic"
    },
    "query_policy_rag": {
        "name": "query_policy_rag",
        "description": "Vector cosine similarity query against ChromaDB climate policy corpus (SEBI BRSR, Carbon Tax, NDMA) to quantify corporate Value-at-Risk.",
        "parameters": {
            "type": "object",
            "properties": {
                "region": {"type": "string", "default": "India"},
                "sector": {"type": "string", "default": "Industrial"},
                "damage_estimate_inr": {"type": "number"}
            },
            "required": ["damage_estimate_inr"]
        },
        "target_agent": "agent-3-financial"
    }
}
