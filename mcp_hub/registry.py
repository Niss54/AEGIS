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
    },
    "anchor_risk_on_chain": {
        "name": "anchor_risk_on_chain",
        "description": "Anchors an Agent 1 risk assessment on Polygon Amoy blockchain via AEGISRiskLedger.sol, creating a tamper-evident on-chain record.",
        "parameters": {
            "type": "object",
            "properties": {
                "lat": {"type": "number", "description": "Latitude"},
                "lon": {"type": "number", "description": "Longitude"},
                "risk_score": {"type": "number", "description": "Agent 1 risk score [0.0 - 1.0]"},
                "ipfs_cid": {"type": "string", "description": "IPFS CIDv1 of full assessment"},
                "location_name": {"type": "string", "description": "Human-readable location label"}
            },
            "required": ["lat", "lon", "risk_score", "ipfs_cid", "location_name"]
        },
        "target_agent": "blockchain-layer"
    },
    "store_on_ipfs": {
        "name": "store_on_ipfs",
        "description": "Stores a climate assessment payload on IPFS via Pinata and returns the CIDv1 content identifier for provenance anchoring.",
        "parameters": {
            "type": "object",
            "properties": {
                "payload": {"type": "object", "description": "JSON payload to store"},
                "filename": {"type": "string", "description": "Logical filename"}
            },
            "required": ["payload"]
        },
        "target_agent": "ipfs-layer"
    },
    "check_bond_trigger": {
        "name": "check_bond_trigger",
        "description": "Notifies DisasterBond contract about a critical assessment. Automatically pays covered beneficiaries if threshold is breached for consecutive cycles.",
        "parameters": {
            "type": "object",
            "properties": {
                "lat": {"type": "number"},
                "lon": {"type": "number"},
                "risk_score_bps": {"type": "integer", "description": "Score in basis points [0 - 10000]"},
                "assessment_id": {"type": "string", "description": "On-chain assessment ID (bytes32)"}
            },
            "required": ["lat", "lon", "risk_score_bps", "assessment_id"]
        },
        "target_agent": "blockchain-layer"
    },
    "check_cfmc_eligibility": {
        "name": "check_cfmc_eligibility",
        "description": "Checks and mints Carbon Flood Mitigation Credits (CFMC) when Agent 1 predicts high risk but Agent 2 demonstrates low damage.",
        "parameters": {
            "type": "object",
            "properties": {
                "lat": {"type": "number"},
                "lon": {"type": "number"},
                "risk_score": {"type": "number"},
                "dem_depth_cm": {"type": "number"},
                "beneficiary": {"type": "string"},
                "assessment_id": {"type": "string"}
            },
            "required": ["lat", "lon", "risk_score", "dem_depth_cm", "beneficiary", "assessment_id"]
        },
        "target_agent": "blockchain-layer"
    }
}
