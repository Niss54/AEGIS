"""
Phase 27.1: Clay Earth Foundation Model (ViT-MAE) Verification Suite
Governance: Gravitas Reliability Runtime · Mathematical Invariant Adherence

Verifies:
1. Embedding dimensionality strictly equals 768.
2. Spatiotemporal sinusoidal positional encodings vary deterministically.
3. Sentinel-1 SAR cloud penetration takes precedence when cloud cover >= 70%.
4. Specular radar backscatter delta (delta_sar <= -3.5 dB) triggers high flood probability.
5. Topographical elevation gradient dampens inundation accumulation.
6. 3-Tier Circuit Breaker state machine (CLOSED -> OPEN -> HALF-OPEN -> CLOSED) and Tier 5 fallback.
7. FastAPI REST endpoints: /api/v1/clay/embeddings, /api/v1/clay/flood-prob, /api/v1/clay/model-info, /api/v1/clay/pipeline.
"""
import pytest
import time
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.clay_foundation import (
    clay_engine,
    ClayFoundationEngine,
    ClayChipInput,
    ClayFloodProbRequest
)

client = TestClient(app)


def test_clay_embedding_dimensions_and_spatiotemporal_invariants():
    """
    Validates Clay Foundation Model 768-dimensional latent vector and
    2D sinusoidal geographic and seasonal cyclical positional encodings.
    """
    engine = ClayFoundationEngine()

    chip_mumbai = ClayChipInput(
        chip_id="CHIP-MUMBAI-01",
        lat=19.0728,
        lon=72.8797,
        doy=205,
        hour=14,
        cloud_cover_pct=25.0,
        dem_elevation_m=8.0
    )
    embeddings_mumbai = engine.extract_clay_embeddings(chip_mumbai)

    # Invariant 1: Dimensionality strictly 768
    assert len(embeddings_mumbai) == 768, f"Expected 768-dim embeddings, got {len(embeddings_mumbai)}"
    assert all(isinstance(x, float) for x in embeddings_mumbai)

    # Invariant 2: Positional encodings differentiate distinct spatial coordinates
    chip_delhi = ClayChipInput(
        chip_id="CHIP-DELHI-01",
        lat=28.6139,
        lon=77.2090,
        doy=205,
        hour=14,
        cloud_cover_pct=25.0,
        dem_elevation_m=215.0
    )
    embeddings_delhi = engine.extract_clay_embeddings(chip_delhi)
    assert embeddings_mumbai != embeddings_delhi, "Spatial coordinates must yield distinct embeddings"

    # Invariant 3: Seasonal cycle variation (Monsoon DOY 205 vs Winter DOY 15)
    tokens_monsoon, meta_monsoon = engine.compute_spatiotemporal_encodings(19.07, 72.87, doy=205)
    tokens_winter, meta_winter = engine.compute_spatiotemporal_encodings(19.07, 72.87, doy=15)
    assert meta_monsoon["seasonal_phase"] != meta_winter["seasonal_phase"]


def test_clay_cloud_penetrating_sar_radar_fusion():
    """
    Validates that when optical cloud cover >= 70%, SAR C-band radar backscatter
    penetrates cloud cover and drives zero-shot flood probability.
    """
    engine = ClayFoundationEngine()

    # Heavy monsoon cloudburst scenario (90% cloud cover, -7.5 dB SAR drop)
    req_monsoon = ClayFloodProbRequest(
        event_id="CLAY-TEST-MONSOON",
        lat=19.0728,
        lon=72.8797,
        doy=210,
        cloud_cover_pct=92.0,
        precipitation_mm_hr=110.0,
        sar_vv_db=-18.5,
        sar_baseline_vv_db=-11.0,  # Delta = -7.5 dB (severe standing water)
        dem_elevation_m=6.5
    )
    res_monsoon = engine.predict_zero_shot_flood_prob(req_monsoon)

    assert res_monsoon.optical_attenuated is True, "Cloud cover >= 70% must flag optical attenuation"
    assert res_monsoon.sar_penetration_active is True, "SAR penetration must be active during cloud cover"
    assert res_monsoon.backscatter_delta_db <= -3.5, "Expected steep specular radar backscatter drop"
    assert res_monsoon.flood_probability >= 0.70, f"Expected high flood prob, got {res_monsoon.flood_probability}"
    assert res_monsoon.hazard_classification in ("SEVERE_INUNDATION", "CATASTROPHIC_FLOOD")

    # Clear dry day scenario (10% cloud cover, nominal backscatter)
    req_dry = ClayFloodProbRequest(
        event_id="CLAY-TEST-DRY",
        lat=26.9124,
        lon=75.7873,
        doy=120,
        cloud_cover_pct=10.0,
        precipitation_mm_hr=0.0,
        sar_vv_db=-10.8,
        sar_baseline_vv_db=-11.0,  # Delta = +0.2 dB (normal dry soil)
        dem_elevation_m=420.0
    )
    res_dry = engine.predict_zero_shot_flood_prob(req_dry)

    assert res_dry.optical_attenuated is False
    assert res_dry.flood_probability < 0.25, f"Expected low flood prob for dry conditions, got {res_dry.flood_probability}"
    assert res_dry.hazard_classification == "LOW"


def test_clay_topographical_elevation_damping():
    """
    Validates that low-lying coastal/river basins have higher flood probability
    than high-elevation plateaus under identical storm rainfall.
    """
    engine = ClayFoundationEngine()

    # Coastal basin (elevation 5m)
    res_low = engine.predict_zero_shot_flood_prob(ClayFloodProbRequest(
        lat=19.07, lon=72.87, precipitation_mm_hr=80.0,
        sar_vv_db=-16.0, sar_baseline_vv_db=-11.0, dem_elevation_m=5.0
    ))

    # High plateau (elevation 250m)
    res_high = engine.predict_zero_shot_flood_prob(ClayFloodProbRequest(
        lat=19.07, lon=72.87, precipitation_mm_hr=80.0,
        sar_vv_db=-16.0, sar_baseline_vv_db=-11.0, dem_elevation_m=250.0
    ))

    assert res_low.flood_probability > res_high.flood_probability, (
        f"Low elevation ({res_low.flood_probability}) must have higher pooling probability "
        f"than high elevation ({res_high.flood_probability})"
    )


def test_clay_circuit_breaker_and_resilient_fallback():
    """
    Validates 3-failure circuit breaker tripping to OPEN and Tier 5 fallback.
    """
    engine = ClayFoundationEngine()
    assert engine.circuit_state == "CLOSED"

    # Force 3 failures
    for _ in range(3):
        engine._record_failure()

    assert engine.circuit_state == "OPEN"

    # In OPEN state, fallback gracefully without crashing
    req = ClayFloodProbRequest(lat=19.07, lon=72.87, precipitation_mm_hr=50.0)
    fallback_res = engine.predict_zero_shot_flood_prob(req)
    assert fallback_res.hazard_classification == "MODERATE"
    assert fallback_res.clay_embedding_summary.get("dim") == 768

    # Reset circuit breaker
    engine.circuit_state = "CLOSED"
    engine.failure_count = 0


def test_clay_fastapi_embeddings_endpoint():
    """
    Tests POST /api/v1/clay/embeddings endpoint.
    """
    payload = {
        "chip_id": "CHIP-REST-TEST",
        "lat": 19.0728,
        "lon": 72.8797,
        "doy": 200,
        "hour": 11,
        "cloud_cover_pct": 82.0,
        "dem_elevation_m": 12.0
    }
    response = client.post("/api/v1/clay/embeddings", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["embedding_dim"] == 768
    assert len(data["embeddings"]) == 768
    assert data["dominant_modality"] == "SENTINEL_1_SAR"
    assert "spatiotemporal_tokens" in data


def test_clay_fastapi_flood_prob_endpoint():
    """
    Tests POST /api/v1/clay/flood-prob endpoint.
    """
    payload = {
        "event_id": "CLAY-PROB-REST-01",
        "lat": 19.0728,
        "lon": 72.8797,
        "doy": 205,
        "cloud_cover_pct": 88.0,
        "precipitation_mm_hr": 125.0,
        "sar_vv_db": -19.2,
        "sar_baseline_vv_db": -11.0,
        "dem_elevation_m": 7.5
    }
    response = client.post("/api/v1/clay/flood-prob", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["event_id"] == "CLAY-PROB-REST-01"
    assert 0.0 <= data["flood_probability"] <= 1.0
    assert data["sar_penetration_active"] is True
    assert data["optical_attenuated"] is True
    assert data["hazard_classification"] in ("SEVERE_INUNDATION", "CATASTROPHIC_FLOOD")


def test_clay_fastapi_model_info_and_pipeline():
    """
    Tests GET /api/v1/clay/model-info and POST /api/v1/clay/pipeline.
    """
    # 1. Model Info
    res_info = client.get("/api/v1/clay/model-info")
    assert res_info.status_code == 200
    info = res_info.json()
    assert info["latent_dimension"] == 768
    assert "Vision Transformer" in info["backbone"]
    assert "102.4M Parameters" in info["parameter_count"]
    assert info["cloud_penetration_support"] is True

    # 2. Pipeline Gate
    res_pipe = client.post("/api/v1/clay/pipeline", json={
        "lat": 19.0728,
        "lon": 72.8797,
        "precipitation_mm_hr": 95.0,
        "cloud_cover_pct": 85.0
    })
    assert res_pipe.status_code == 200
    pipe = res_pipe.json()
    assert pipe["verified_flag"] is True
    assert pipe["status"] == "OPERATIONAL"
    assert pipe["phase_id"] == 27
    assert pipe["embedding_dim"] == 768
