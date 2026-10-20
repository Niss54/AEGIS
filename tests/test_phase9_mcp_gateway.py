"""
TERRA-SENTINEL Production Verification: Phase 9
Suite: Model Context Protocol (MCP) Hub & JSON-RPC 2.0 Gateway
Governance: Gravitas Reliability Runtime · Machine-Checked Evidence Protocol
"""
import pytest
import time
from fastapi.testclient import TestClient

from mcp_hub.controller import MCPGatewayController, MCPToolModel
from mcp_hub.hub import app as hub_app
from mcp_hub.stdio_server import handle_rpc_message
from mcp_hub.registry import TOOLS_REGISTRY


@pytest.fixture
def controller():
    return MCPGatewayController()


@pytest.fixture
def client():
    return TestClient(hub_app)


# ============================================================================
# 1. PRD Invariant & Pipeline Execution Tests
# ============================================================================

@pytest.mark.asyncio
async def test_phase_9_execution_invariant(controller):
    """
    PRD Invariant Test: Verifies MCPToolModel generation and operational metadata.
    """
    sample_payload = {"event_id": "TEST-PHASE-9-INV", "telemetry": 42.0, "region": "mumbai"}
    result = await controller.execute_phase_pipeline(sample_payload)

    assert isinstance(result, MCPToolModel)
    assert result.event_id == "TEST-PHASE-9-INV"
    assert result.verified_flag is True
    assert result.execution_tier == "ENTERPRISE_PROD"
    assert result.metadata["status"] == "OPERATIONAL"
    assert result.metadata["phase_id"] == 9
    assert result.metadata["registered_tool_count"] == len(TOOLS_REGISTRY)
    assert result.metadata["circuit_state"] == "CLOSED"
    assert "fetch_weather_vectors" in result.metadata["tools_available"]


@pytest.mark.asyncio
async def test_phase_9_empty_payload_rejection(controller):
    """
    PRD Boundary Test: Empty payload must be strictly rejected.
    """
    with pytest.raises(ValueError, match="Empty payload rejected"):
        await controller.execute_phase_pipeline({})


# ============================================================================
# 2. Circuit Breaker Resilience & State Machine
# ============================================================================

@pytest.mark.asyncio
async def test_phase_9_circuit_breaker_trip_and_recovery(controller):
    """
    Resilience Test: 3 consecutive failures trip circuit to OPEN.
    Probe after cooldown switches to HALF-OPEN, and success resets to CLOSED.
    """
    assert controller.circuit_state == "CLOSED"
    assert controller.failure_count == 0

    # Simulate 3 failures
    controller._record_failure()
    assert controller.failure_count == 1
    assert controller.circuit_state == "CLOSED"

    controller._record_failure()
    assert controller.failure_count == 2
    assert controller.circuit_state == "CLOSED"

    controller._record_failure()
    assert controller.failure_count == 3
    assert controller.circuit_state == "OPEN"

    # In OPEN state during cooldown, calls are blocked
    with pytest.raises(RuntimeError, match="Circuit Breaker is OPEN"):
        controller._check_circuit_breaker()

    # Fast forward time beyond cooldown
    controller.last_failure_time = time.time() - (controller.cooldown_period_sec + 5)
    controller._check_circuit_breaker()
    assert controller.circuit_state == "HALF-OPEN"

    # Execution success in HALF-OPEN resets circuit to CLOSED
    sample_payload = {"event_id": "RECOVERY-EVENT", "status": "probe"}
    res = await controller.execute_phase_pipeline(sample_payload)
    assert res.event_id == "RECOVERY-EVENT"
    assert controller.circuit_state == "CLOSED"
    assert controller.failure_count == 0


# ============================================================================
# 3. JSON-RPC 2.0 Envelope Validation
# ============================================================================

def test_json_rpc_envelope_validation(controller):
    """
    Verifies strict adherence to JSON-RPC 2.0 RFC specifications.
    """
    # Missing or invalid jsonrpc version
    valid, err = controller.validate_rpc_envelope({"jsonrpc": "1.0", "method": "initialize"})
    assert not valid
    assert err["code"] == -32600

    # Missing method
    valid, err = controller.validate_rpc_envelope({"jsonrpc": "2.0"})
    assert not valid
    assert err["code"] == -32600

    # Non-string method
    valid, err = controller.validate_rpc_envelope({"jsonrpc": "2.0", "method": 12345})
    assert not valid
    assert err["code"] == -32600

    # Valid envelope
    valid, err = controller.validate_rpc_envelope({"jsonrpc": "2.0", "method": "initialize"})
    assert valid
    assert err is None


# ============================================================================
# 4. MCP Hub REST & Pipeline API Endpoints
# ============================================================================

def test_mcp_health_endpoint(client):
    """Verifies GET /mcp/health reports protocol and tool registry status."""
    resp = client.get("/mcp/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["protocol"] == "JSON-RPC 2.0"
    assert data["registered_tools_count"] == len(TOOLS_REGISTRY)


def test_mcp_tools_catalog_endpoint(client):
    """Verifies GET /mcp/tools returns catalog of all registered tools with schemas."""
    resp = client.get("/mcp/tools")
    assert resp.status_code == 200
    data = resp.json()
    tools = data["tools"]
    assert len(tools) >= 5
    tool_names = [t["name"] for t in tools]
    assert "fetch_weather_vectors" in tool_names
    assert "run_flood_classifier" in tool_names
    assert "compute_dem_exposure" in tool_names
    assert "query_policy_rag" in tool_names


def test_mcp_pipeline_endpoint(client):
    """Verifies POST /mcp/pipeline executes Phase 9 pipeline and returns MCPToolModel."""
    payload = {
        "event_id": "TEST-REST-PIPELINE",
        "station_id": "IN-MUM-01",
        "rainfall_mm": 125.4
    }
    resp = client.post("/mcp/pipeline", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["event_id"] == "TEST-REST-PIPELINE"
    assert data["verified_flag"] is True
    assert data["execution_tier"] == "ENTERPRISE_PROD"
    assert data["metadata"]["status"] == "OPERATIONAL"
    assert data["metadata"]["registered_tool_count"] == len(TOOLS_REGISTRY)


# ============================================================================
# 5. MCP JSON-RPC 2.0 Handshake, Discovery, & Tool Invocation
# ============================================================================

def test_mcp_rpc_initialize(client):
    """Verifies official MCP 'initialize' handshake."""
    req = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {},
        "id": "handshake-1"
    }
    resp = client.post("/mcp/invoke", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == "handshake-1"
    result = data["result"]
    assert result["protocolVersion"] == "2024-11-05"
    assert result["serverInfo"]["name"] in ["aegis-climate-mcp-hub", "terra-sentinel-mcp-hub"]


def test_mcp_rpc_tools_list(client):
    """Verifies official MCP 'tools/list' tool discovery method."""
    req = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": "discovery-1"
    }
    resp = client.post("/mcp/invoke", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert "result" in data
    tools = data["result"]["tools"]
    assert len(tools) >= 5
    tool_names = [t["name"] for t in tools]
    assert "fetch_weather_vectors" in tool_names


def test_mcp_rpc_tools_call_success(client):
    """Verifies official MCP 'tools/call' invocation with registered tool."""
    req = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "check_cfmc_eligibility",
            "arguments": {
                "risk_score": 0.85,
                "dem_depth_cm": 10.0
            }
        },
        "id": "call-1"
    }
    resp = client.post("/mcp/invoke", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "call-1"
    assert "result" in data
    assert data["result"]["isError"] is False
    assert data["result"]["data"]["eligible"] is True
    assert data["result"]["data"]["reward_amount"] == 100


def test_mcp_rpc_tools_call_unknown_tool(client):
    """Verifies unknown tool in 'tools/call' returns -32601 Method Not Found."""
    req = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "non_existent_tool_xyz",
            "arguments": {}
        },
        "id": "call-err-1"
    }
    resp = client.post("/mcp/invoke", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert data["error"]["code"] == -32601
    assert "not found" in data["error"]["message"]


def test_mcp_rpc_invalid_jsonrpc_version(client):
    """Verifies invalid jsonrpc field returns -32600 Invalid Request."""
    req = {
        "jsonrpc": "1.0",
        "method": "initialize",
        "params": {},
        "id": "ver-err"
    }
    resp = client.post("/mcp/invoke", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert data["error"]["code"] == -32600


# ============================================================================
# 6. Stdio Transport Server Verification
# ============================================================================

def test_stdio_server_handler_initialize():
    """Verifies stdio_server handle_rpc_message for MCP initialize."""
    msg = {"jsonrpc": "2.0", "method": "initialize", "params": {}, "id": "stdio-1"}
    resp = handle_rpc_message(msg)
    assert resp["jsonrpc"] == "2.0"
    assert resp["id"] == "stdio-1"
    assert resp["result"]["protocolVersion"] == "2024-11-05"


def test_stdio_server_handler_tool_call():
    """Verifies stdio_server handle_rpc_message for tools/call."""
    msg = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "check_cfmc_eligibility",
            "arguments": {"risk_score": 0.20, "dem_depth_cm": 5.0}
        },
        "id": "stdio-2"
    }
    resp = handle_rpc_message(msg)
    assert resp["id"] == "stdio-2"
    assert resp["result"]["isError"] is False
