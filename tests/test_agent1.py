"""
AEGIS-CLIMATE — Agent 1 (Acute Physical Risk ML) Test Suite
Validates model artifact loading, inference accuracy, latency, and MCP tool execution.
"""
import sys
import os
import time

sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.agent1_ml import flood_ml_engine
from mcp_hub.hub import app as mcp_app

backend_client = TestClient(app)
mcp_client = TestClient(mcp_app)


def test_model_loaded():
    """Verify trained model artifact and metadata."""
    assert flood_ml_engine.is_trained() is True, "Model should be loaded from flood_classifier.pkl"
    assert flood_ml_engine.metadata is not None
    accuracy = flood_ml_engine.metadata.get("accuracy", 0.0)
    assert accuracy >= 0.90, f"Expected accuracy >= 0.90, got {accuracy}"
    print(f"[PASS] Model loaded successfully: Accuracy={accuracy*100:.2f}%, CV-F1={flood_ml_engine.metadata.get('cv_f1_mean')}")


def test_arid_low_risk_inference():
    """Verify dry/arid conditions classify as LOW risk."""
    t0 = time.time()
    res = flood_ml_engine.predict(
        soil_saturation_pct=15.0,
        precipitation_24h_mm=0.0,
        precipitation_7d_mm=5.0,
        relative_humidity_pct=25.0,
        elevation_m=450.0,
        drainage_capacity_index=80.0
    )
    latency_ms = (time.time() - t0) * 1000
    assert res["risk_tier"] == "LOW"
    assert res["risk_score"] < 0.40
    assert latency_ms < 50.0, f"Inference too slow: {latency_ms:.2f}ms"
    print(f"[PASS] Arid conditions classified as LOW (Score={res['risk_score']}, Latency={latency_ms:.2f}ms)")


def test_monsoon_cloudburst_critical_inference():
    """Verify extreme monsoon cloudburst classifies as CRITICAL/HIGH risk."""
    res = flood_ml_engine.predict(
        soil_saturation_pct=95.0,
        precipitation_24h_mm=135.0,
        precipitation_7d_mm=320.0,
        relative_humidity_pct=94.0,
        elevation_m=8.0,
        drainage_capacity_index=35.0
    )
    assert res["risk_tier"] in ["CRITICAL", "HIGH"]
    assert res["risk_score"] >= 0.75
    assert "probabilities" in res
    assert res["probabilities"]["CRITICAL"] > 0.30 or res["probabilities"]["HIGH"] > 0.30
    print(f"[PASS] Cloudburst classified as {res['risk_tier']} (Score={res['risk_score']}, Dominant={res['dominant_factor']})")


def test_tools_predict_endpoint():
    """Test POST /api/v1/tools/predict REST endpoint."""
    payload = {
        "soil_saturation_pct": 88.0,
        "precipitation_24h_mm": 90.0,
        "precipitation_7d_mm": 210.0,
        "relative_humidity_pct": 89.0,
        "elevation_m": 12.0,
        "drainage_capacity_index": 50.0
    }
    res = backend_client.post("/api/v1/tools/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "risk_score" in data
    assert "risk_tier" in data
    assert "probabilities" in data
    print(f"[PASS] /api/v1/tools/predict endpoint working: Risk={data['risk_tier']} (Score={data['risk_score']})")


def test_model_info_endpoint():
    """Test GET /api/v1/tools/model-info endpoint."""
    res = backend_client.get("/api/v1/tools/model-info")
    assert res.status_code == 200
    data = res.json()
    assert data["is_trained"] is True
    assert "feature_importances" in data["metadata"]
    print(f"[PASS] /api/v1/tools/model-info endpoint returned metadata with {len(data['metadata']['feature_importances'])} features")


def test_mcp_hub_integration():
    """Test calling run_flood_classifier through MCP Hub JSON-RPC 2.0."""
    rpc_payload = {
        "jsonrpc": "2.0",
        "method": "run_flood_classifier",
        "params": {
            "soil_saturation_pct": 92.0,
            "precipitation_24h_mm": 85.0,
            "precipitation_7d_mm": 200.0,
            "relative_humidity_pct": 88.0,
            "elevation_m": 10.0,
            "drainage_capacity_index": 45.0
        },
        "id": "mcp-test-agent1"
    }
    res = mcp_client.post("/mcp/invoke", json=rpc_payload)
    assert res.status_code == 200
    resp_data = res.json()
    assert "result" in resp_data
    result = resp_data["result"]
    assert "risk_score" in result
    assert result["risk_tier"] in ["HIGH", "CRITICAL"]
    print(f"[PASS] MCP Hub JSON-RPC dispatch: Tool returned tier={result['risk_tier']} score={result['risk_score']}")


if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING AGENT 1 (ML CORE) TEST SUITE")
    print("=" * 60)
    test_model_loaded()
    test_arid_low_risk_inference()
    test_monsoon_cloudburst_critical_inference()
    test_tools_predict_endpoint()
    test_model_info_endpoint()
    test_mcp_hub_integration()
    print("=" * 60)
    print(">>> ALL AGENT 1 ML CORE TESTS PASSED WITH 100% SUCCESS! <<<")
    print("=" * 60)
