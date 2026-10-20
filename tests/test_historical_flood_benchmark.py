"""
Automated Pytest Suite: Real-World Historical Flood Disaster Benchmark
Validates model prediction accuracy against empirical IMD/CWC/GloFAS meteorological ground truth.
Enforces:
1. 100% Catastrophic Disaster Detection Recall (Mumbai 2005, Kerala 2018, Chennai 2015, Assam 2022).
2. 0% False Positives on Dry-Season Baselines (Mumbai, Delhi, Bengaluru, Chennai).
"""
import pytest
from backend.app.agent1_ml import FloodRiskMLModel
from scripts.benchmark_historical_floods import HISTORICAL_FLOOD_BENCHMARK


@pytest.fixture(scope="module")
def ml_model():
    model = FloodRiskMLModel()
    assert model.is_trained() is True, "FloodRiskMLModel must be loaded from serialized weights"
    return model


@pytest.mark.parametrize("event", HISTORICAL_FLOOD_BENCHMARK, ids=[e["event_id"] for e in HISTORICAL_FLOOD_BENCHMARK])
def test_historical_flood_event_prediction(ml_model, event):
    """Verifies each real historical event is accurately categorized by physical severity."""
    pred = ml_model.predict(
        soil_saturation_pct=event["soil_saturation_pct"],
        precipitation_24h_mm=event["precipitation_24h_mm"],
        precipitation_7d_mm=event["precipitation_7d_mm"],
        relative_humidity_pct=event["relative_humidity_pct"],
        elevation_m=event["elevation_m"],
        drainage_capacity_index=event["drainage_capacity_index"]
    )

    expected = event["ground_truth_severity"]
    predicted_tier = pred["risk_tier"]
    score = pred["risk_score"]

    if expected == "CRITICAL":
        assert predicted_tier in ["CRITICAL", "HIGH"], f"Catastrophic event {event['name']} must trigger >= HIGH risk, got {predicted_tier}"
        assert score >= 0.70, f"Score for {event['name']} must be >= 0.70, got {score}"
    elif expected == "HIGH":
        assert predicted_tier in ["HIGH", "CRITICAL"], f"High risk event {event['name']} must trigger >= HIGH risk, got {predicted_tier}"
        assert score >= 0.65, f"Score for {event['name']} must be >= 0.65, got {score}"
    elif expected == "MEDIUM":
        assert predicted_tier in ["MEDIUM", "HIGH", "LOW"], f"Moderate event {event['name']} got {predicted_tier}"
        assert 0.20 <= score <= 0.85
    elif expected == "LOW":
        assert predicted_tier == "LOW", f"Baseline control {event['name']} must predict LOW, got {predicted_tier}"
        assert score < 0.40, f"Baseline control {event['name']} score must be < 0.40, got {score}"


def test_zero_false_alarm_rate_invariant(ml_model):
    """Enforces zero false alarm rate on dry baseline observations."""
    controls = [e for e in HISTORICAL_FLOOD_BENCHMARK if e["ground_truth_severity"] == "LOW"]
    assert len(controls) >= 4, "Must have at least 4 baseline control observations"
    for c in controls:
        pred = ml_model.predict(
            soil_saturation_pct=c["soil_saturation_pct"],
            precipitation_24h_mm=c["precipitation_24h_mm"],
            precipitation_7d_mm=c["precipitation_7d_mm"],
            relative_humidity_pct=c["relative_humidity_pct"],
            elevation_m=c["elevation_m"],
            drainage_capacity_index=c["drainage_capacity_index"]
        )
        assert pred["risk_tier"] == "LOW"
        assert pred["risk_score"] < 0.30
