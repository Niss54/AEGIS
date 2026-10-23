"""
AEGIS-CLIMATE Phase 18 Verification Test Suite
Mission-Control Cockpit: React 19 + TypeScript + Leaflet CartoDB 60fps
Governance: Gravitas Reliability Runtime · Mathematical Invariant Verification
"""
import time
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.web_cockpit import (
    WebCockpitController,
    FrontendViewModel,
    evaluate_frame_budget,
    optimize_gis_contour_vectors
)
from mcp_hub.hub import execute_tool_logic


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_phase_18_execution_invariant():
    """
    Verification Target: PRD Phase 18 Invariant Gate.
    Asserts FrontendViewModel schema validation, 60fps frame budget tracking, and operational metadata.
    """
    controller = WebCockpitController()
    sample_payload = {
        "event_id": "TEST-PHASE-18",
        "render_time_ms": 14.2,
        "vertex_count": 680,
        "location": "Mumbai Mithi River Basin"
    }
    result = await controller.execute_phase_pipeline(sample_payload)
    assert isinstance(result, FrontendViewModel)
    assert result.event_id == "TEST-PHASE-18"
    assert result.verified_flag is True
    assert result.metadata["status"] == "OPERATIONAL"
    assert result.metadata["phase_id"] == 18
    assert "frame_budget_evaluation" in result.metadata
    fb_eval = result.metadata["frame_budget_evaluation"]
    assert fb_eval["is_60fps"] is True
    assert fb_eval["fps"] >= 60.0


@pytest.mark.asyncio
async def test_phase_18_empty_payload_rejection():
    """Asserts that empty payload is rejected with ValueError."""
    controller = WebCockpitController()
    with pytest.raises(ValueError) as excinfo:
        await controller.execute_phase_pipeline({})
    assert "Empty payload rejected" in str(excinfo.value)


def test_mathematical_governing_equation_frame_budget():
    """
    Governing Equation Invariant:
        FrameBudget <= 16.67ms ==> FPS >= 60
    """
    # Case 1: High performance sub-16.67ms frame
    res1 = evaluate_frame_budget(render_time_ms=12.5, vertex_count=450)
    assert res1.is_60fps is True
    assert res1.fps == 80.0
    assert res1.budget_utilization_pct < 100.0
    assert res1.degradation_risk == "NONE"
    assert res1.recommended_simplification is False

    # Case 2: Near boundary 16.0ms frame
    res2 = evaluate_frame_budget(render_time_ms=16.0, vertex_count=1200)
    assert res2.is_60fps is True
    assert res2.fps == 62.5
    assert res2.degradation_risk == "NONE"

    # Case 3: Moderate degradation (30 - 60 FPS range)
    res3 = evaluate_frame_budget(render_time_ms=25.0, vertex_count=3500)
    assert res3.is_60fps is False
    assert res3.fps == 40.0
    assert res3.degradation_risk == "MODERATE"
    assert res3.recommended_simplification is True
    assert res3.optimal_target_vertices <= 2500

    # Case 4: Critical frame drop (< 30 FPS)
    res4 = evaluate_frame_budget(render_time_ms=50.0, vertex_count=5000)
    assert res4.is_60fps is False
    assert res4.fps == 20.0
    assert res4.degradation_risk == "CRITICAL"
    assert res4.recommended_simplification is True


def test_gis_contour_vector_optimization():
    """
    Verifies that high-density GeoJSON contours (> 3000 vertices)
    are decimated to protect the 60fps frame budget while maintaining closed polygon rings.
    """
    # Build a synthetic high-density contour with 4000 vertices
    ring = []
    base_lat, base_lon = 19.0728, 72.8797
    vertex_count = 4000
    for i in range(vertex_count):
        lat = base_lat + 0.01 * (i / vertex_count)
        lon = base_lon + 0.01 * (i / vertex_count)
        ring.append([lon, lat])
    ring.append(ring[0])  # Close ring

    geojson_input = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [ring]
                },
                "properties": {"zone": "Inundation Contour"}
            }
        ]
    }

    opt_result = optimize_gis_contour_vectors(geojson_input, max_vertices=2000)
    assert opt_result["optimized"] is True
    assert opt_result["original_vertices"] > 4000
    assert opt_result["result_vertices"] <= 2500
    assert opt_result["reduction_pct"] > 0.0

    # Verify polygon ring remains valid and closed
    res_ring = opt_result["features"][0]["geometry"]["coordinates"][0]
    assert res_ring[0] == res_ring[-1]


@pytest.mark.asyncio
async def test_circuit_breaker_transitions():
    """
    Verifies 3-tier circuit breaker:
    CLOSED -> (3 failures) -> OPEN -> (cooldown) -> HALF_OPEN -> (success) -> CLOSED.
    """
    controller = WebCockpitController()
    controller.cooldown_period = 0.2  # 200ms
    assert controller.circuit_state == "CLOSED"

    # Simulate 3 consecutive failures
    controller._record_failure("GIS render timeout 1")
    controller._record_failure("GIS render timeout 2")
    assert controller.circuit_state == "CLOSED"
    controller._record_failure("GIS render timeout 3")
    assert controller.circuit_state == "OPEN"

    # In OPEN state, pipeline routes to fallback
    res_open = await controller.execute_phase_pipeline({
        "event_id": "TEST-FALLBACK",
        "render_time_ms": 35.0,
        "vertex_count": 5000
    })
    assert res_open.execution_tier == "LOCAL_FALLBACK"

    # Cooldown expires -> HALF_OPEN
    time.sleep(0.25)
    assert controller._evaluate_circuit_state() == "HALF_OPEN"

    # Successful request resets state to CLOSED
    controller._record_success()
    assert controller.circuit_state == "CLOSED"
    assert controller.failure_count == 0


def test_rest_cockpit_endpoints(client):
    """Verifies FastAPI REST endpoints under /cockpit and /api/v1/cockpit."""
    # 1. Health check
    resp_h = client.get("/cockpit/phase18/health")
    assert resp_h.status_code == 200
    data_h = resp_h.json()
    assert data_h["status"] == "healthy"
    assert data_h["phase"] == 18

    # 2. Frame budget evaluate endpoint
    eval_payload = {
        "render_time_ms": 14.0,
        "vertex_count": 520,
        "dom_nodes": 115,
        "active_layers": ["core_basin", "asset_pins"]
    }
    resp_eval = client.post("/cockpit/frame-budget/evaluate", json=eval_payload)
    assert resp_eval.status_code == 200
    data_eval = resp_eval.json()
    assert data_eval["is_60fps"] is True
    assert data_eval["fps"] >= 60.0

    # 3. Pipeline endpoint
    resp_pipe = client.post("/cockpit/phase18/pipeline", json=eval_payload)
    assert resp_pipe.status_code == 200
    data_pipe = resp_pipe.json()
    assert data_pipe["verified_flag"] is True
    assert data_pipe["metadata"]["status"] == "OPERATIONAL"

    # 4. State endpoint
    resp_state = client.get("/cockpit/state")
    assert resp_state.status_code == 200
    data_state = resp_state.json()
    assert data_state["target_fps"] == 60
    assert "CartoDB.DarkMatter" in data_state["active_tileset"]


def test_mcp_cockpit_tools():
    """Verifies MCP JSON-RPC tool dispatches for Phase 18."""
    # 1. evaluate_cockpit_frame_budget
    res1 = execute_tool_logic("evaluate_cockpit_frame_budget", {
        "render_time_ms": 15.5,
        "vertex_count": 600
    })
    assert res1["is_60fps"] is True
    assert res1["fps"] >= 60.0

    # 2. get_mission_control_cockpit_state
    res2 = execute_tool_logic("get_mission_control_cockpit_state", {})
    assert res2["target_fps"] == 60
    assert res2["status"] == "OPERATIONAL"

    # 3. optimize_gis_contour_vectors
    test_poly = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[72.8, 19.0], [72.9, 19.0], [72.9, 19.1], [72.8, 19.1], [72.8, 19.0]]]
                }
            }
        ]
    }
    res3 = execute_tool_logic("optimize_gis_contour_vectors", {
        "geojson_data": test_poly,
        "max_vertices": 3000
    })
    assert "features" in res3
    assert res3["optimized"] is False  # Already under threshold
