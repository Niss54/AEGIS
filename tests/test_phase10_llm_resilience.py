"""
TERRA-SENTINEL Production Verification: Phase 10
Suite: Multi-Model LLM Resilience & Automated Circuit Breaker Failover
Governance: Gravitas Reliability Runtime · Machine-Checked Evidence Protocol
"""
import pytest
import time
from fastapi.testclient import TestClient

from backend.app.main import app as backend_app
from backend.app.llm_circuit import LLMCircuitController, LLMFailoverModel, TierCircuitBreaker
from mcp_hub.hub import app as hub_app


@pytest.fixture
def controller():
    return LLMCircuitController()


@pytest.fixture
def client():
    return TestClient(backend_app)


@pytest.fixture
def mcp_client():
    return TestClient(hub_app)


# ============================================================================
# 1. PRD Invariant & Pipeline Execution Tests
# ============================================================================

@pytest.mark.asyncio
async def test_phase_10_execution_invariant(controller):
    """
    PRD Invariant Test: Verifies LLMFailoverModel generation and operational metadata.
    """
    sample_payload = {"event_id": "TEST-PHASE-10", "telemetry": 42.0}
    result = await controller.execute_phase_pipeline(sample_payload)

    assert isinstance(result, LLMFailoverModel)
    assert result.event_id == "TEST-PHASE-10"
    assert result.verified_flag is True
    assert result.execution_tier == "ENTERPRISE_PROD"
    assert result.metadata["status"] == "OPERATIONAL"
    assert result.metadata["phase_id"] == 10
    assert result.metadata["tiers_online"] == 5
    assert result.metadata["tiers_tripped"] == 0
    assert "State(t) = OPEN if Failures_60s >= 3 else CLOSED" in result.metadata["mathematical_invariant"]


@pytest.mark.asyncio
async def test_phase_10_empty_payload_rejection(controller):
    """
    PRD Boundary Test: Empty payload must be strictly rejected.
    """
    with pytest.raises(ValueError, match="Empty payload rejected"):
        await controller.execute_phase_pipeline({})


# ============================================================================
# 2. Circuit Breaker State Machine & Mathematical Invariant
# ============================================================================

def test_tier_circuit_breaker_mathematical_invariant():
    """
    Verifies: State(t) = OPEN if Failures_60s >= 3 else CLOSED.
    Tests rolling 60s failure tracking, 30s probe cooldown, and HALF-OPEN probe recovery.
    """
    breaker = TierCircuitBreaker(1, "Test Gemini", "Google", "gemini-2.0-flash")
    assert breaker.state == "CLOSED"
    assert breaker.can_attempt() is True

    # 1st failure: remains CLOSED
    breaker.record_failure("Transient 503")
    assert breaker.state == "CLOSED"
    assert breaker.can_attempt() is True

    # 2nd failure: remains CLOSED
    breaker.record_failure("Transient 429")
    assert breaker.state == "CLOSED"
    assert breaker.can_attempt() is True

    # 3rd failure within 60s: trips to OPEN
    breaker.record_failure("Upstream timeout")
    assert breaker.state == "OPEN"
    assert breaker.can_attempt() is False

    # Within cooldown period (<30s), requests are denied
    assert breaker.can_attempt() is False

    # Advance time beyond 30s cooldown
    breaker.last_failure_time = time.time() - (breaker.cooldown_period_sec + 2)
    assert breaker.can_attempt() is True
    assert breaker.state == "HALF-OPEN"

    # Successful canary probe resets state to CLOSED
    breaker.record_success()
    assert breaker.state == "CLOSED"
    assert len(breaker.failure_timestamps) == 0


def test_tier_circuit_breaker_half_open_failure_reversion():
    """
    Verifies that a failure during HALF-OPEN state immediately re-trips the circuit to OPEN.
    """
    breaker = TierCircuitBreaker(2, "Test Groq", "Groq Inc.", "llama-3.3-70b")
    # Force to HALF-OPEN
    breaker.state = "OPEN"
    breaker.last_failure_time = time.time() - 35.0
    assert breaker.can_attempt() is True
    assert breaker.state == "HALF-OPEN"

    # Failure during probe immediately reverts to OPEN
    breaker.record_failure("Probe failed")
    assert breaker.state == "OPEN"
    assert breaker.can_attempt() is False


# ============================================================================
# 3. 5-Tier Hierarchical Resilience & Graceful Degradation
# ============================================================================

def test_route_prompt_primary_tier(controller, monkeypatch):
    """Verifies default routing to Tier 1 when all tiers are healthy."""
    class MockResponse:
        status_code = 200
        def json(self):
            return {"candidates": [{"content": {"parts": [{"text": "Synthetic Gemini Alert Assessment"}]}}]}

    import httpx
    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: MockResponse())

    res = controller.route_prompt("Evaluate flood warning for Mumbai Kurla")
    assert res["active_tier"] == 1
    assert "Google Vertex AI" in res["provider"] or "Google Cloud" in res["provider"]
    assert len(res["text"]) > 0
    assert res["circuit_state"] == "CLOSED"


def test_route_prompt_failover_to_tier_2(controller):
    """Verifies automatic failover from Tier 1 to Tier 2 when Tier 1 fails."""
    res = controller.route_prompt(
        "Evaluate rainfall spike",
        mock_failures=[1]
    )
    assert res["active_tier"] == 2
    assert "Groq" in res["provider"]
    assert res["failover_route"][0]["tier_id"] == 1
    assert res["failover_route"][0]["status"] == "FAILED_MOCK_TRIPPED"
    assert res["failover_route"][1]["tier_id"] == 2
    assert res["failover_route"][1]["status"] == "SUCCESS"


def test_route_prompt_catastrophic_failover_to_tier_5(controller):
    """
    Catastrophic Resilience Test:
    When ALL cloud tiers (1, 2, 3, 4) fail simultaneously,
    the platform seamlessly degrades to Tier 5 (Local Deterministic Heuristic Engine).
    Zero downtime, 100% operational guarantee!
    """
    res = controller.route_prompt(
        "Urgent inundation assessment",
        mock_failures=[1, 2, 3, 4],
        context={"location": "Dharavi Mithi Basin", "risk_score": 0.88, "waterlogging_depth_cm": 65}
    )
    assert res["active_tier"] == 5
    assert "Local Deterministic" in res["provider"] or "TERRA-SENTINEL Internal" in res["provider"]
    assert "Dharavi Mithi Basin" in res["text"]
    assert "88%" in res["text"]
    assert "65cm" in res["text"]
    assert len(res["failover_route"]) == 5


def test_bilingual_hindi_devanagari_tier_5_fallback(controller):
    """Verifies Tier 5 produces authentic Devanagari Hindi civil warnings for vernacular communities."""
    res = controller.route_prompt(
        "generate hindi devanagari warning alert",
        mock_failures=[1, 2, 3, 4],
        context={"location": "कुर्ला पश्चिम", "risk_score": 0.92, "waterlogging_depth_cm": 75}
    )
    assert res["active_tier"] == 5
    assert "चेतावनी" in res["text"]
    assert "कुर्ला पश्चिम" in res["text"]
    assert "92%" in res["text"]


# ============================================================================
# 4. REST API Gateway Endpoints
# ============================================================================

def test_api_circuit_status_endpoint(client):
    """Verifies GET /api/v1/llm/circuit-status returns metrics for all 5 tiers."""
    resp = client.get("/api/v1/llm/circuit-status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["phase_id"] == 10
    assert len(data["tiers"]) == 5
    tier_names = [t["name"] for t in data["tiers"]]
    assert any("Vertex AI" in name for name in tier_names)
    assert any("Groq" in name for name in tier_names)
    assert any("Claude" in name for name in tier_names)
    assert any("OpenAI" in name for name in tier_names)
    assert any("Local Deterministic" in name for name in tier_names)


def test_api_route_prompt_endpoint(client):
    """Verifies POST /api/v1/llm/route-prompt dispatches through circuit breaker."""
    payload = {
        "prompt": "NDMA urban drainage status query",
        "preferred_tier": 1,
        "context": {"location": "Bandra Kurla Complex", "risk_score": 0.65}
    }
    resp = client.post("/api/v1/llm/route-prompt", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["active_tier"] in (1, 2, 3, 4, 5)
    assert "text" in data
    assert "latency_ms" in data


def test_api_pipeline_endpoint(client):
    """Verifies POST /api/v1/llm/pipeline returns compliant LLMFailoverModel."""
    payload = {"event_id": "TEST-REST-LLM-PIPE", "region": "Maharashtra"}
    resp = client.post("/api/v1/llm/pipeline", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["event_id"] == "TEST-REST-LLM-PIPE"
    assert data["verified_flag"] is True
    assert data["execution_tier"] == "ENTERPRISE_PROD"
    assert data["metadata"]["status"] == "OPERATIONAL"


def test_api_reset_circuits_endpoint(client):
    """Verifies POST /api/v1/llm/reset-circuits resets all breakers to CLOSED."""
    resp = client.post("/api/v1/llm/reset-circuits")
    assert resp.status_code == 200
    assert resp.json()["status"] == "SUCCESS"


# ============================================================================
# 5. Model Context Protocol (MCP) Tool Integration
# ============================================================================

def test_mcp_route_llm_resilient_prompt_tool(mcp_client):
    """Verifies MCP Hub /mcp/invoke executes route_llm_resilient_prompt tool."""
    rpc_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "route_llm_resilient_prompt",
            "arguments": {
                "prompt": "Evaluate municipal drainage status",
                "preferred_tier": 1
            }
        },
        "id": "mcp-llm-1"
    }
    resp = mcp_client.post("/mcp/invoke", json=rpc_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "mcp-llm-1"
    assert "result" in data
    assert data["result"]["isError"] is False
    assert data["result"]["data"]["active_tier"] in (1, 2, 3, 4, 5)
