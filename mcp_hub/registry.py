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
    "analyze_satellite_imagery": {
        "name": "analyze_satellite_imagery",
        "description": "Multimodal satellite Earth observation pipeline ingesting Copernicus Sentinel-2 MSI (NDWI/NDVI), ISRO Bhuvan NRSC geology, and Google Earth Engine DEM rasters to run Gemini 2.0 Flash spatial reasoning.",
        "parameters": {
            "type": "object",
            "properties": {
                "lat": {"type": "number", "description": "Target latitude"},
                "lon": {"type": "number", "description": "Target longitude"},
                "location_name": {"type": "string", "default": "Target Corridor"},
                "depth_cm": {"type": "number", "default": 85}
            },
            "required": ["lat", "lon"]
        },
        "target_agent": "agent-2-chronic"
    },
    "compute_hydraulic_flow_accumulation": {
        "name": "compute_hydraulic_flow_accumulation",
        "description": "Simulates municipal stormwater drainage network throughput, hydraulic flow accumulation, and chokepoints using Saint-Venant depth curves: D_water = max(0, (P_eff - C_drain)/10) * (1 + 1/(1+Slope)).",
        "parameters": {
            "type": "object",
            "properties": {
                "precipitation_mm_hr": {"type": "number", "description": "Rainfall intensity in mm/hr"},
                "drainage_capacity_mm_hr": {"type": "number", "default": 35.0},
                "soil_saturation_pct": {"type": "number", "default": 80.0},
                "slope_gradient": {"type": "number", "default": 0.02},
                "lat": {"type": "number", "default": 19.0760},
                "lon": {"type": "number", "default": 72.8777}
            },
            "required": ["precipitation_mm_hr"]
        },
        "target_agent": "agent-2-chronic"
    },
    "run_monte_carlo_financial_var": {
        "name": "run_monte_carlo_financial_var",
        "description": "Executes Monte Carlo stochastic simulation over N >= 1000 iterations to compute enterprise Value-at-Risk percentiles (VaR 95, VaR 99, Expected Shortfall CVaR) and RBI LTV haircuts: VaR_95 = Percentile_95(sum V_asset * (1 - e^{-lambda * D})).",
        "parameters": {
            "type": "object",
            "properties": {
                "waterlogging_depth_cm": {"type": "number", "description": "Inundation depth in cm"},
                "risk_score": {"type": "number", "description": "Physical hazard score [0.0 - 1.0]"},
                "num_simulations": {"type": "integer", "default": 1000}
            },
            "required": ["waterlogging_depth_cm", "risk_score"]
        },
        "target_agent": "agent-3-financial"
    },
    "query_hybrid_rag_fusion": {
        "name": "query_hybrid_rag_fusion",
        "description": "Executes Dual-Retriever Hybrid RAG fusing dense semantic vectors and BM25 Okapi sparse keyword frequencies via Reciprocal Rank Fusion (RRF k=60): RRF(d) = 0.55/(60 + r_dense) + 0.45/(60 + r_sparse).",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Natural language statutory or regulatory question"},
                "top_k": {"type": "integer", "default": 3}
            },
            "required": ["query"]
        },
        "target_agent": "agent-3-financial"
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
    },
    "route_llm_resilient_prompt": {
        "name": "route_llm_resilient_prompt",
        "description": "5-Tier hierarchical LLM circuit breaker router executing prompts across Vertex AI Gemini, Groq, Claude, OpenAI, and local deterministic heuristics.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Prompt to evaluate"},
                "preferred_tier": {"type": "integer", "description": "Preferred starting tier (1 to 5)", "default": 1}
            },
            "required": ["prompt"]
        },
        "target_agent": "resilience-orchestrator"
    },
    "verify_telemetry_seal": {
        "name": "verify_telemetry_seal",
        "description": "Zero-Trust cryptographic HMAC-SHA256 signature verifier and anti-replay validator for IoT environmental telemetry packets.",
        "parameters": {
            "type": "object",
            "properties": {
                "station_id": {"type": "string"},
                "payload": {"type": "object"},
                "signature": {"type": "string"},
                "timestamp_epoch": {"type": "number"},
                "nonce": {"type": "string"}
            },
            "required": ["station_id", "payload", "signature", "timestamp_epoch", "nonce"]
        },
        "target_agent": "security-layer"
    },
    "sync_offline_mutations": {
        "name": "sync_offline_mutations",
        "description": "Multi-tier bi-directional offline synchronization tool reconciling queued client mutations with cloud L1/L2 data stores.",
        "parameters": {
            "type": "object",
            "properties": {
                "device_id": {"type": "string"},
                "client_state": {"type": "object"},
                "records": {"type": "array", "items": {"type": "object"}}
            },
            "required": ["device_id", "records"]
        },
        "target_agent": "storage-layer"
    },
    "check_token_bucket_rate_limit": {
        "name": "check_token_bucket_rate_limit",
        "description": "Enforces deterministic token bucket rate limit adhering to Tokens(t) = min(C, Tokens(t_0) + r * (t - t_0)) with Redis/memory state.",
        "parameters": {
            "type": "object",
            "properties": {
                "identifier": {"type": "string", "description": "Client, IP, or station identifier"},
                "cost": {"type": "number", "description": "Token cost for operation", "default": 1.0},
                "capacity": {"type": "number", "description": "Burst capacity limit override"},
                "refill_rate": {"type": "number", "description": "Refill rate override (tokens/sec)"}
            },
            "required": ["identifier"]
        },
        "target_agent": "rate-limiting-gateway"
    },
    "get_distributed_cache_value": {
        "name": "get_distributed_cache_value",
        "description": "Retrieves cached risk assessments, weather vectors, or telemetry from Redis distributed memory cache.",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Cache key to look up"}
            },
            "required": ["key"]
        },
        "target_agent": "caching-layer"
    },
    "set_distributed_cache_value": {
        "name": "set_distributed_cache_value",
        "description": "Sets a key-value pair in the distributed Redis cache with TTL seconds.",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Cache key"},
                "value": {"description": "Value to store"},
                "ttl_seconds": {"type": "integer", "description": "TTL in seconds", "default": 300}
            },
            "required": ["key", "value"]
        },
        "target_agent": "caching-layer"
    },
    "publish_pubsub_event": {
        "name": "publish_pubsub_event",
        "description": "Publishes a real-time event across the distributed Redis Pub/Sub cluster.",
        "parameters": {
            "type": "object",
            "properties": {
                "channel": {"type": "string", "description": "Pub/sub channel name"},
                "message": {"type": "object", "description": "JSON message payload"}
            },
            "required": ["channel", "message"]
        },
        "target_agent": "pubsub-bus"
    },
    "compute_onchain_keccak_hash": {
        "name": "compute_onchain_keccak_hash",
        "description": "Calculates deterministic on-chain hash satisfying Hash_onchain = keccak256(Hotspot || VaR || IPFS_CID).",
        "parameters": {
            "type": "object",
            "properties": {
                "hotspot": {"type": "string", "description": "Hotspot location name"},
                "var_amount": {"type": "number", "description": "Value-at-Risk financial exposure in INR lakhs"},
                "ipfs_cid": {"type": "string", "description": "IPFS content identifier"}
            },
            "required": ["hotspot", "var_amount", "ipfs_cid"]
        },
        "target_agent": "blockchain-audit-layer"
    },
    "anchor_assessment_to_ledger": {
        "name": "anchor_assessment_to_ledger",
        "description": "Anchors verified environmental risk assessment to Polygon Amoy smart contract ledger with Keccak256 hash and IPFS CID.",
        "parameters": {
            "type": "object",
            "properties": {
                "hotspot": {"type": "string", "description": "Location name"},
                "var_amount": {"type": "number", "description": "VaR financial exposure"},
                "ipfs_cid": {"type": "string", "description": "IPFS CIDv1 string"},
                "risk_score": {"type": "number", "description": "Aggregate acute risk score (0.0 to 1.0)"},
                "lat": {"type": "number", "description": "Latitude coordinate"},
                "lon": {"type": "number", "description": "Longitude coordinate"}
            },
            "required": ["hotspot", "var_amount", "ipfs_cid", "risk_score", "lat", "lon"]
        },
        "target_agent": "blockchain-audit-layer"
    },
    "verify_onchain_anchor": {
        "name": "verify_onchain_anchor",
        "description": "Verifies cryptographic proof and existence of an on-chain disaster risk assessment in the ledger.",
        "parameters": {
            "type": "object",
            "properties": {
                "assessment_id": {"type": "string", "description": "On-chain assessment ID or Keccak256 hash"}
            },
            "required": ["assessment_id"]
        },
        "target_agent": "blockchain-audit-layer"
    },
    "evaluate_parametric_trigger": {
        "name": "evaluate_parametric_trigger",
        "description": "Evaluates parametric disaster insurance condition Trigger(D) = I_{D >= D_threshold} => Payout(Beneficiary) based on waterlogging depth and risk score.",
        "parameters": {
            "type": "object",
            "properties": {
                "depth_cm": {"type": "number", "description": "Waterlogging / flood depth in cm"},
                "threshold_cm": {"type": "number", "description": "Trigger threshold depth in cm", "default": 50.0},
                "risk_score_bps": {"type": "integer", "description": "Risk score in BPS (0-10000)", "default": 7000},
                "threshold_risk_bps": {"type": "integer", "description": "Critical risk threshold in BPS", "default": 6500},
                "principal_usd": {"type": "number", "description": "Bond notional principal USD", "default": 100000.0},
                "coverage_limit_usd": {"type": "number", "description": "Maximum contractual coverage payout USD", "default": 250000.0}
            },
            "required": ["depth_cm"]
        },
        "target_agent": "parametric-insurance-layer"
    },
    "settle_parametric_bond": {
        "name": "settle_parametric_bond",
        "description": "Executes automated parametric smart bond settlement on Polygon Amoy or Tier 2 local fallback.",
        "parameters": {
            "type": "object",
            "properties": {
                "bond_id": {"type": "string", "description": "Unique bond identifier"},
                "assessment_id": {"type": "string", "description": "Assessment event ID"},
                "depth_cm": {"type": "number", "description": "Flood depth in cm"},
                "risk_score_bps": {"type": "integer", "description": "Risk score in BPS"},
                "beneficiary": {"type": "string", "description": "Payout recipient address"},
                "payout_amount_usd": {"type": "number", "description": "Optional payout override USD"},
                "force_fallback": {"type": "boolean", "description": "Force Tier 2 circuit fallback", "default": False}
            },
            "required": ["bond_id", "assessment_id", "depth_cm", "risk_score_bps", "beneficiary"]
        },
        "target_agent": "parametric-insurance-layer"
    },
    "evaluate_cfmc_mitigation_reward": {
        "name": "evaluate_cfmc_mitigation_reward",
        "description": "Evaluates and issues Carbon Flood Mitigation Credits (CFMC) when acute physical risk >= 0.65 (CRITICAL) but local DEM flood depth < 20cm.",
        "parameters": {
            "type": "object",
            "properties": {
                "beneficiary": {"type": "string", "description": "Mitigation sponsor address"},
                "assessment_id": {"type": "string", "description": "Assessment event ID"},
                "risk_score_bps": {"type": "integer", "description": "Risk score in BPS (0-10000)"},
                "dem_depth_cm": {"type": "number", "description": "DEM water depth in cm"},
                "lat": {"type": "number", "description": "Latitude coordinate", "default": 19.0728},
                "lon": {"type": "number", "description": "Longitude coordinate", "default": 72.8797}
            },
            "required": ["beneficiary", "assessment_id", "risk_score_bps", "dem_depth_cm"]
        },
        "target_agent": "carbon-credit-layer"
    },
    "compute_satellite_spectral_indices": {
        "name": "compute_satellite_spectral_indices",
        "description": "Calculates NDWI = (Green - NIR)/(Green + NIR) and NDVI = (NIR - Red)/(NIR + Red) multispectral indices from Sentinel-2 bands.",
        "parameters": {
            "type": "object",
            "properties": {
                "green": {"type": "number", "description": "Sentinel-2 B03 Green reflectance (0.0 to 1.0)"},
                "red": {"type": "number", "description": "Sentinel-2 B04 Red reflectance (0.0 to 1.0)"},
                "nir": {"type": "number", "description": "Sentinel-2 B08 NIR reflectance (0.0 to 1.0)"},
                "swir": {"type": "number", "description": "Optional Sentinel-2 B11 SWIR reflectance"}
            },
            "required": ["green", "red", "nir"]
        },
        "target_agent": "earth-observation-pipeline"
    },
    "ingest_earth_observation_telemetry": {
        "name": "ingest_earth_observation_telemetry",
        "description": "Ingests Copernicus Sentinel-2 MSI L2A metadata, ISRO Bhuvan NRSC geological basin layers, and GEE SRTM 30m DEM.",
        "parameters": {
            "type": "object",
            "properties": {
                "lat": {"type": "number", "description": "Latitude coordinate", "default": 19.0728},
                "lon": {"type": "number", "description": "Longitude coordinate", "default": 72.8797},
                "elevation_m": {"type": "number", "description": "Surface elevation in meters", "default": 12.0}
            },
            "required": ["lat", "lon"]
        },
        "target_agent": "earth-observation-pipeline"
    },
    "analyze_satellite_imagery": {
        "name": "analyze_satellite_imagery",
        "description": "Executes Gemini 2.0 Flash multimodal spatial reasoning over Sentinel-2 multispectral rasters, DEM elevation contours, and telemetry.",
        "parameters": {
            "type": "object",
            "properties": {
                "lat": {"type": "number", "description": "Latitude coordinate", "default": 19.0728},
                "lon": {"type": "number", "description": "Longitude coordinate", "default": 72.8797},
                "location_name": {"type": "string", "description": "Asset or corridor location name", "default": "Target Corridor"},
                "depth_cm": {"type": "integer", "description": "Physical inundation depth in cm", "default": 85}
            },
            "required": ["lat", "lon"]
        },
        "target_agent": "earth-observation-pipeline"
    },
    "generate_bilingual_civic_advisory": {
        "name": "generate_bilingual_civic_advisory",
        "description": "Synthesizes emergency civic advisories in English and Devanagari Hindi using Google Vertex AI Gemini 2.0 Flash with hierarchical failover.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Hotspot location name", "default": "Mumbai Mithi River Basin"},
                "effective_precip_mm": {"type": "number", "description": "Effective 24h precipitation in mm", "default": 95.0},
                "waterlogging_depth_cm": {"type": "integer", "description": "Projected waterlogging depth in cm", "default": 85},
                "buildings_at_risk": {"type": "integer", "description": "Number of critical structures exposed", "default": 340},
                "var_inr": {"type": "number", "description": "Enterprise Value-at-Risk in INR", "default": 250000000.0},
                "policy_context": {"type": "string", "description": "Retrieved statutory policy context", "default": ""},
                "generate_speech": {"type": "boolean", "description": "Generate neural TTS audio", "default": False}
            },
            "required": ["location"]
        },
        "target_agent": "civic-advisory-generator"
    },
    "synthesize_civic_speech": {
        "name": "synthesize_civic_speech",
        "description": "Synthesizes neural voice audio for emergency broadcasts using Sarvam AI (Devanagari Hindi) or ElevenLabs (English).",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Advisory text string to synthesize"},
                "language": {"type": "string", "description": "Language code ('hi' or 'en')", "default": "hi"},
                "speaker": {"type": "string", "description": "Voice speaker name", "default": "priya"}
            },
            "required": ["text"]
        },
        "target_agent": "civic-advisory-generator"
    },
    "validate_civic_advisory_bounds": {
        "name": "validate_civic_advisory_bounds",
        "description": "Validates and clamps civic telemetry inputs (precipitation, waterlogging depth, buildings at risk, VaR) against realistic physical operational bounds.",
        "parameters": {
            "type": "object",
            "properties": {
                "effective_precip_mm": {"type": "number", "description": "Effective 24h precipitation in mm", "default": 95.0},
                "waterlogging_depth_cm": {"type": "integer", "description": "Projected waterlogging depth in cm", "default": 85},
                "buildings_at_risk": {"type": "integer", "description": "Number of critical structures exposed", "default": 340},
                "var_inr": {"type": "number", "description": "Enterprise Value-at-Risk in INR", "default": 250000000.0}
            },
            "required": []
        },
        "target_agent": "civic-advisory-generator"
    },
    "evaluate_cockpit_frame_budget": {
        "name": "evaluate_cockpit_frame_budget",
        "description": "Evaluates GIS cockpit render time against the 60fps frame budget invariant (FrameBudget <= 16.67ms ==> FPS >= 60).",
        "parameters": {
            "type": "object",
            "properties": {
                "render_time_ms": {"type": "number", "description": "Measured frame render duration in ms", "default": 12.5},
                "vertex_count": {"type": "integer", "description": "Total vertices in active GIS layers", "default": 450}
            },
            "required": ["render_time_ms"]
        },
        "target_agent": "mission-control-cockpit"
    },
    "get_mission_control_cockpit_state": {
        "name": "get_mission_control_cockpit_state",
        "description": "Returns real-time mission-control cockpit GIS configuration, active overlays, tileset status, and frame targets.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        },
        "target_agent": "mission-control-cockpit"
    },
    "optimize_gis_contour_vectors": {
        "name": "optimize_gis_contour_vectors",
        "description": "Downsamples and decimates high-density GeoJSON contours to prevent 60fps frame budget violations.",
        "parameters": {
            "type": "object",
            "properties": {
                "geojson_data": {"type": "object", "description": "GeoJSON FeatureCollection"},
                "max_vertices": {"type": "integer", "description": "Maximum vertex budget", "default": 3000}
            },
            "required": ["geojson_data"]
        },
        "target_agent": "mission-control-cockpit"
    },
    "evaluate_edge_offline_availability": {
        "name": "evaluate_edge_offline_availability",
        "description": "Evaluates edge network resilience and verifies Availability = 100% (Cached Shell ⊕ Local Heuristics).",
        "parameters": {
            "type": "object",
            "properties": {
                "is_online": {"type": "boolean", "description": "Network connectivity status", "default": True},
                "has_cached_shell": {"type": "boolean", "description": "Service worker cache shell status", "default": True},
                "has_local_heuristics": {"type": "boolean", "description": "Local deterministic heuristics status", "default": True}
            },
            "required": ["is_online"]
        },
        "target_agent": "edge-network-resilience"
    },
    "get_pwa_edge_manifest": {
        "name": "get_pwa_edge_manifest",
        "description": "Returns PWA service worker caching metadata, cache version, and offline survival capabilities.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        },
        "target_agent": "edge-network-resilience"
    },
    "reconcile_edge_offline_queue": {
        "name": "reconcile_edge_offline_queue",
        "description": "Processes and reconciles client mutation queue buffered during network partitions.",
        "parameters": {
            "type": "object",
            "properties": {
                "mutations": {"type": "array", "description": "List of queued offline mutations", "default": []}
            },
            "required": []
        },
        "target_agent": "edge-network-resilience"
    },
    "evaluate_container_image_budget": {
        "name": "evaluate_container_image_budget",
        "description": "Evaluates container image size and zero-vulnerability security gate against mathematical invariant: ImageSize <= 250MB, Vulnerabilities = 0.",
        "parameters": {
            "type": "object",
            "properties": {
                "image_size_mb": {"type": "number", "description": "Image size in megabytes", "default": 215.0},
                "vulnerability_count": {"type": "integer", "description": "Known CVE vulnerability count", "default": 0},
                "non_root_user": {"type": "boolean", "description": "Whether non-root user UID 10001 is active", "default": True}
            },
            "required": ["image_size_mb"]
        },
        "target_agent": "container-packaging-controller"
    },
    "get_cloud_run_deployment_spec": {
        "name": "get_cloud_run_deployment_spec",
        "description": "Returns production Google Cloud Run serverless deployment specification and resource limits.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        },
        "target_agent": "container-packaging-controller"
    },
    "inspect_dockerfile_security_layers": {
        "name": "inspect_dockerfile_security_layers",
        "description": "Statically analyzes Dockerfile to verify multi-stage architecture, unprivileged non-root user (UID 10001), healthcheck, and no-cache flags.",
        "parameters": {
            "type": "object",
            "properties": {
                "dockerfile_path": {"type": "string", "description": "Optional custom Dockerfile path", "default": ""}
            },
            "required": []
        },
        "target_agent": "container-packaging-controller"
    },
    "validate_ci_pipeline_step": {
        "name": "validate_ci_pipeline_step",
        "description": "Enforces Phase 21 CI/CD governing invariant: GitPush(main) ==> Test ==> Build ==> Deploy(CloudRun).",
        "parameters": {
            "type": "object",
            "properties": {
                "steps": {
                    "type": "array",
                    "description": "List of pipeline step identifiers in proposed execution order",
                    "default": ["test", "build", "push", "deploy"]
                },
                "branch": {"type": "string", "description": "Triggering git branch name", "default": "main"}
            },
            "required": ["steps"]
        },
        "target_agent": "cloud-build-ci-controller"
    },
    "get_cloud_build_configuration": {
        "name": "get_cloud_build_configuration",
        "description": "Parses and returns static verification of cloudbuild.yaml structure, step IDs, timeout, and deployment target.",
        "parameters": {
            "type": "object",
            "properties": {
                "yaml_path": {"type": "string", "description": "Optional custom cloudbuild.yaml path", "default": ""}
            },
            "required": []
        },
        "target_agent": "cloud-build-ci-controller"
    },
    "simulate_git_push_ci_trigger": {
        "name": "simulate_git_push_ci_trigger",
        "description": "Simulates Git Push CI/CD trigger to evaluate automated action (BUILD_AND_DEPLOY vs TEST_ONLY).",
        "parameters": {
            "type": "object",
            "properties": {
                "branch": {"type": "string", "description": "Triggering git branch name", "default": "main"},
                "commit_sha": {"type": "string", "description": "Commit SHA hash", "default": "HEAD"}
            },
            "required": []
        },
        "target_agent": "cloud-build-ci-controller"
    },
    "evaluate_edge_performance_budget": {
        "name": "evaluate_edge_performance_budget",
        "description": "Evaluates edge CDN latency and audit score against mathematical invariant: TTFB_global <= 80ms, LighthouseScore >= 98.",
        "parameters": {
            "type": "object",
            "properties": {
                "ttfb_ms": {"type": "number", "description": "Time To First Byte latency in milliseconds", "default": 45.0},
                "lighthouse_score": {"type": "integer", "description": "Google Lighthouse composite audit score", "default": 99},
                "edge_region": {"type": "string", "description": "Vercel edge point-of-presence code", "default": "bom1"}
            },
            "required": ["ttfb_ms", "lighthouse_score"]
        },
        "target_agent": "vercel-edge-controller"
    },
    "inspect_vercel_edge_configuration": {
        "name": "inspect_vercel_edge_configuration",
        "description": "Statically inspects vercel.json for reverse proxy rewrites, immutable caching headers, and HSTS security.",
        "parameters": {
            "type": "object",
            "properties": {
                "config_path": {"type": "string", "description": "Optional custom vercel.json path", "default": ""}
            },
            "required": []
        },
        "target_agent": "vercel-edge-controller"
    },
    "get_edge_cdn_routing_matrix": {
        "name": "get_edge_cdn_routing_matrix",
        "description": "Returns production Anycast Edge CDN point-of-presence topology, latency SLAs, and HTTP/3 QUIC protocol status.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        },
        "target_agent": "vercel-edge-controller"
    },
    "evaluate_test_quality_gate": {
        "name": "evaluate_test_quality_gate",
        "description": "Evaluates automated test suite pass rate against Phase 23 governing invariant: Passed >= 52 / 52 (100% Pass Rate), Failed = 0.",
        "parameters": {
            "type": "object",
            "properties": {
                "passed_count": {"type": "integer", "description": "Total passed test assertions", "default": 62},
                "failed_count": {"type": "integer", "description": "Total failed test assertions", "default": 0},
                "skipped_count": {"type": "integer", "description": "Total skipped test assertions", "default": 0}
            },
            "required": ["passed_count"]
        },
        "target_agent": "quality-gate-controller"
    },
    "discover_test_suites_audit": {
        "name": "discover_test_suites_audit",
        "description": "Statically discovers and catalogs all test files, test functions, and phase coverage mapping across the repository.",
        "parameters": {
            "type": "object",
            "properties": {
                "dir_path": {"type": "string", "description": "Optional custom tests directory path", "default": ""}
            },
            "required": []
        },
        "target_agent": "quality-gate-controller"
    },
    "get_quality_assurance_metrics": {
        "name": "get_quality_assurance_metrics",
        "description": "Returns operational quality assurance status, discovered test volume, and circuit breaker health.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        },
        "target_agent": "quality-gate-controller"
    },
    "evaluate_screenplay_timing_budget": {
        "name": "evaluate_screenplay_timing_budget",
        "description": "Evaluates video demo screenplay act timings against Phase 24 governing invariant: Delta_t = 30s + 60s + 60s + 30s = 180s.",
        "parameters": {
            "type": "object",
            "properties": {
                "act1_crisis_s": {"type": "number", "description": "Act 1 duration (The Crisis)", "default": 30.0},
                "act2_ui_s": {"type": "number", "description": "Act 2 duration (Cockpit UI & Live Multi-Agent Cascade)", "default": 60.0},
                "act3_cloud_s": {"type": "number", "description": "Act 3 duration (Google Cloud Tech Alignment & MCP)", "default": 60.0},
                "act4_roi_s": {"type": "number", "description": "Act 4 duration (JAPAC ROI & IEEE ClimateChain Global Demonstration)", "default": 30.0}
            },
            "required": ["act1_crisis_s", "act2_ui_s", "act3_cloud_s", "act4_roi_s"]
        },
        "target_agent": "screenplay-controller"
    },
    "audit_demo_script_screenplay": {
        "name": "audit_demo_script_screenplay",
        "description": "Statically parses docs/DEMO_SCRIPT.md to verify Act structure, Google Cloud keywords, word count, and speech pacing.",
        "parameters": {
            "type": "object",
            "properties": {
                "script_path": {"type": "string", "description": "Optional custom DEMO_SCRIPT.md path", "default": ""}
            },
            "required": []
        },
        "target_agent": "screenplay-controller"
    },
    "get_teleprompter_cue_sheet": {
        "name": "get_teleprompter_cue_sheet",
        "description": "Returns structured teleprompter cues with visual anchors, technical keywords, and timestamp ranges.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        },
        "target_agent": "screenplay-controller"
    },
    "evaluate_tam_sam_som_market_opportunity": {
        "name": "evaluate_tam_sam_som_market_opportunity",
        "description": "Evaluates TAM/SAM/SOM market sizing against Phase 25 governing invariant: TAM = $12.8B, SAM = $3.2B, SOM = $480M.",
        "parameters": {
            "type": "object",
            "properties": {
                "tam_usd_b": {"type": "number", "description": "Total Addressable Market in billions USD", "default": 12.8},
                "sam_usd_b": {"type": "number", "description": "Serviceable Addressable Market in billions USD", "default": 3.2},
                "som_usd_m": {"type": "number", "description": "Serviceable Obtainable Market in millions USD", "default": 480.0}
            },
            "required": ["tam_usd_b", "sam_usd_b", "som_usd_m"]
        },
        "target_agent": "finale-strategy-controller"
    },
    "audit_pitch_deck_slides": {
        "name": "audit_pitch_deck_slides",
        "description": "Statically parses docs/PITCH_DECK.md to verify 10 canonical investor slides, Google Cloud differentiators, and IEEE ClimateChain Global Demonstration roadmap.",
        "parameters": {
            "type": "object",
            "properties": {
                "deck_path": {"type": "string", "description": "Optional custom PITCH_DECK.md path", "default": ""}
            },
            "required": []
        },
        "target_agent": "finale-strategy-controller"
    },
    "get_singapore_grand_finale_playbook": {
        "name": "get_singapore_grand_finale_playbook",
        "description": "Returns structured 48-Hour Live Demo Execution Playbook for the IEEE ClimateChain Global Demonstration stage.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_name": {"type": "string", "description": "Target championship event name", "default": "IEEE ClimateChain 2026 Global Final"}
            },
            "required": []
        },
        "target_agent": "finale-strategy-controller"
    },
    "predict_compound_landslide_flood_hazard": {
        "name": "predict_compound_landslide_flood_hazard",
        "description": "Evaluates Compound Flood & Landslide Susceptibility Index (CFLSI) coupling rainfall, river level, soil saturation, and DEM slope gradient, returning trilingual public safety guidance in English, Urdu (اردو), and Hindi (देवनागरी).",
        "parameters": {
            "type": "object",
            "properties": {
                "rainfall_mm": {"type": "number", "description": "24-hour rainfall in mm"},
                "river_level_m": {"type": "number", "description": "River stage in meters"},
                "soil_moisture_pct": {"type": "number", "description": "Soil saturation percentage"},
                "slope_deg": {"type": "number", "description": "Terrain slope in degrees"},
                "location_name": {"type": "string", "description": "Target corridor or station name", "default": "Western Ghats Slope Corridor"}
            },
            "required": ["rainfall_mm", "river_level_m", "soil_moisture_pct", "slope_deg"]
        },
        "target_agent": "sailab-landslide-agent"
    },
    "delineate_catchment_twi": {
        "name": "delineate_catchment_twi",
        "description": "Executes Deltares HydroMT computational hydrography, D8 steepest-descent flow direction routing, upslope contributing area accumulation, Topographic Wetness Index (TWI = ln(alpha / (tan(beta) + 1e-4))), and Manning overland velocity.",
        "parameters": {
            "type": "object",
            "properties": {
                "basin_id": {"type": "string", "description": "Basin ID (mumbai_mithi, bengaluru_vrishabhavathi, delhi_yamuna, assam_brahmaputra, chennai_adyar)", "default": "mumbai_mithi"},
                "grid_size": {"type": "integer", "description": "DEM grid dimension NxN", "default": 8},
                "cell_resolution_m": {"type": "number", "description": "Spatial grid cell resolution in meters", "default": 30.0},
                "inflow_precipitation_mm": {"type": "number", "description": "Rainfall inflow depth in mm", "default": 95.0},
                "land_cover": {"type": "string", "description": "Land cover class", "default": "URBAN_IMPERVIOUS"}
            },
            "required": ["basin_id"]
        },
        "target_agent": "hydromt-hydrography-agent"
    },
    "verify_satellite_carbon_mrv": {
        "name": "verify_satellite_carbon_mrv",
        "description": "Executes Panda Protocol satellite algorithmic carbon MRV: measures Sentinel-2 multi-spectral NDVI canopy growth, derives dry biomass (tons C), calculates stoichiometric sequestered CO2e (tCO2e = Delta_Biomass * 44/12), and generates Polygon Amoy verification proof hash.",
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "Project ID (prj_mumbai_mangrove, prj_sundarbans_delta, prj_western_ghats, prj_delhi_aravali, prj_bengaluru_lakes)", "default": "prj_mumbai_mangrove"},
                "baseline_ndvi": {"type": "number", "description": "Baseline NDVI at t0"},
                "current_ndvi": {"type": "number", "description": "Current Sentinel-2 NDVI at t1"},
                "canopy_coverage_factor": {"type": "number", "description": "Canopy fraction [0.0, 1.0]"},
                "beneficiary_wallet": {"type": "string", "description": "Beneficiary EVM wallet address", "default": "0x71C8364860D4e0223E4c38AcEbA218175f78235C"}
            },
            "required": ["project_id"]
        },
        "target_agent": "panda-carbon-mrv-agent"
    },
    "scan_ecological_threats": {
        "name": "scan_ecological_threats",
        "description": "Executes Sentinel Flood-Watch multi-temporal change detection (NDBI concrete expansion, NDVI canopy clearing, MNDWI wetland shrinkage) and computes Ecological Threat Index: ETI = 0.45*Delta_NDBI + 0.35*(-Delta_NDVI) + 0.20*(-Delta_MNDWI).",
        "parameters": {
            "type": "object",
            "properties": {
                "site_id": {"type": "string", "description": "Ecological site ID (site_mithi_mangrove, site_bellandur_wetland, site_yamuna_oza, site_deepor_beel, site_pallikaranai_marsh)", "default": "site_mithi_mangrove"},
                "current_ndbi": {"type": "number", "description": "Observed NDBI at t1"},
                "current_ndvi": {"type": "number", "description": "Observed NDVI at t1"},
                "current_mndwi": {"type": "number", "description": "Observed MNDWI at t1"},
                "notes": {"type": "string", "description": "Mission telemetry notes", "default": ""}
            },
            "required": ["site_id"]
        },
        "target_agent": "sentinel-floodwatch-agent"
    }
}



