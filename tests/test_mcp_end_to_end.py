"""
End-to-End Test Suite for AEGIS Model Context Protocol (MCP) Server
Validates JSON-RPC 2.0 and official MCP Specification Compliance on Port 8001 and Port 8000.
"""
import httpx
import json

MCP_STANDALONE_URL = "http://127.0.0.1:8001"
BACKEND_MCP_URL = "http://127.0.0.1:8000"


def test_mcp_health_standalone():
    """Verify MCP Hub standalone service health endpoint."""
    resp = httpx.get(f"{MCP_STANDALONE_URL}/mcp/health", timeout=5.0)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["protocol"] == "JSON-RPC 2.0"
    assert data["registered_tools_count"] >= 4
    assert "fetch_weather_vectors" in data["tools"]
    assert "run_flood_classifier" in data["tools"]
    assert "compute_dem_exposure" in data["tools"]
    assert "query_policy_rag" in data["tools"]


def test_mcp_health_backend_mounted():
    """Verify MCP Hub mounted router on main backend."""
    resp = httpx.get(f"{BACKEND_MCP_URL}/mcp/health", timeout=5.0)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["protocol"] == "JSON-RPC 2.0"


def test_mcp_rest_tools_catalog():
    """Verify REST tools catalog endpoint lists all tools and input schemas."""
    resp = httpx.get(f"{MCP_STANDALONE_URL}/mcp/tools", timeout=5.0)
    assert resp.status_code == 200
    data = resp.json()
    tools = {t["name"]: t for t in data["tools"]}
    assert "fetch_weather_vectors" in tools
    assert "run_flood_classifier" in tools
    assert "compute_dem_exposure" in tools
    assert "query_policy_rag" in tools
    assert tools["run_flood_classifier"]["target_agent"] == "agent-1-acute"
    assert tools["compute_dem_exposure"]["target_agent"] == "agent-2-chronic"
    assert tools["query_policy_rag"]["target_agent"] == "agent-3-financial"


def test_mcp_handshake_initialize():
    """Verify official MCP protocol 'initialize' handshake."""
    payload = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"}
        },
        "id": "init-req-1"
    }
    resp = httpx.post(f"{MCP_STANDALONE_URL}/mcp/invoke", json=payload, timeout=5.0)
    assert resp.status_code == 200
    res = resp.json()
    assert res["jsonrpc"] == "2.0"
    assert res["id"] == "init-req-1"
    result = res["result"]
    assert result["protocolVersion"] == "2024-11-05"
    assert result["serverInfo"]["name"] == "aegis-climate-mcp-hub"


def test_mcp_protocol_tools_list():
    """Verify official MCP protocol 'tools/list' tool discovery."""
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": "list-req-1"
    }
    resp = httpx.post(f"{MCP_STANDALONE_URL}/mcp/invoke", json=payload, timeout=5.0)
    assert resp.status_code == 200
    res = resp.json()
    assert res["jsonrpc"] == "2.0"
    assert "tools" in res["result"]
    tool_names = [t["name"] for t in res["result"]["tools"]]
    assert "fetch_weather_vectors" in tool_names
    assert "run_flood_classifier" in tool_names


def test_mcp_protocol_tools_call_weather():
    """Verify official MCP protocol 'tools/call' for fetch_weather_vectors."""
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "fetch_weather_vectors",
            "arguments": {"lat": 19.0760, "lon": 72.8777}
        },
        "id": "call-req-1"
    }
    resp = httpx.post(f"{MCP_STANDALONE_URL}/mcp/invoke", json=payload, timeout=8.0)
    assert resp.status_code == 200
    res = resp.json()
    assert res["jsonrpc"] == "2.0"
    assert res["id"] == "call-req-1"
    assert not res["result"].get("isError", True)
    assert "data" in res["result"]
    data = res["result"]["data"]
    assert "precipitation_24h_mm" in data
    assert "soil_saturation_pct" in data


def test_mcp_direct_invoke_flood_classifier():
    """Verify direct JSON-RPC 2.0 tool execution for run_flood_classifier (Agent 1)."""
    payload = {
        "jsonrpc": "2.0",
        "method": "run_flood_classifier",
        "params": {
            "precipitation_24h_mm": 115.0,
            "precipitation_7d_mm": 280.0,
            "soil_saturation_pct": 88.5,
            "relative_humidity_pct": 92.0,
            "elevation_m": 8.0,
            "drainage_capacity_index": 55.0
        },
        "id": "rpc-flood-1"
    }
    resp = httpx.post(f"{MCP_STANDALONE_URL}/mcp/invoke", json=payload, timeout=15.0)
    assert resp.status_code == 200
    res = resp.json()
    assert res["jsonrpc"] == "2.0"
    assert res["id"] == "rpc-flood-1"
    result = res["result"]
    assert "risk_score" in result
    assert result["risk_score"] > 0.6  # High risk expected for heavy rain
    assert "risk_tier" in result


def test_mcp_direct_invoke_dem_exposure():
    """Verify direct JSON-RPC 2.0 tool execution for compute_dem_exposure (Agent 2)."""
    payload = {
        "jsonrpc": "2.0",
        "method": "compute_dem_exposure",
        "params": {
            "lat": 19.0728,
            "lon": 72.8797,
            "risk_score": 0.82,
            "precipitation_24h_mm": 120.0,
            "soil_saturation_pct": 89.0,
            "elevation_m": 9.0,
            "radius_km": 10.0
        },
        "id": "rpc-dem-1"
    }
    resp = httpx.post(f"{MCP_STANDALONE_URL}/mcp/invoke", json=payload, timeout=15.0)
    assert resp.status_code == 200
    res = resp.json()
    assert res["jsonrpc"] == "2.0"
    assert res["id"] == "rpc-dem-1"
    result = res["result"]
    assert "exposure_tier" in result
    assert "waterlogging_depth_cm" in result
    assert result["waterlogging_depth_cm"] > 0


def test_mcp_direct_invoke_policy_rag():
    """Verify direct JSON-RPC 2.0 tool execution for query_policy_rag (Agent 3)."""
    payload = {
        "jsonrpc": "2.0",
        "method": "query_policy_rag",
        "params": {
            "query": "SEBI BRSR Principle 6 flood disclosures and penalty clauses"
        },
        "id": "rpc-rag-1"
    }
    resp = httpx.post(f"{MCP_STANDALONE_URL}/mcp/invoke", json=payload, timeout=15.0)
    assert resp.status_code == 200
    res = resp.json()
    assert res["jsonrpc"] == "2.0"
    assert res["id"] == "rpc-rag-1"
    result = res["result"]
    assert "applicable_regulations" in result
    assert len(result["applicable_regulations"]) > 0


def test_mcp_error_handling_unknown_method():
    """Verify standard JSON-RPC 2.0 code -32601 on unknown method."""
    payload = {
        "jsonrpc": "2.0",
        "method": "non_existent_unregistered_tool",
        "params": {},
        "id": "rpc-err-1"
    }
    resp = httpx.post(f"{MCP_STANDALONE_URL}/mcp/invoke", json=payload, timeout=5.0)
    assert resp.status_code == 200
    res = resp.json()
    assert res["jsonrpc"] == "2.0"
    assert res["id"] == "rpc-err-1"
    assert "error" in res
    assert res["error"]["code"] == -32601


if __name__ == "__main__":
    print("Running end-to-end MCP Server test suite...")
    test_mcp_health_standalone()
    print("[PASS] test_mcp_health_standalone passed")
    test_mcp_health_backend_mounted()
    print("[PASS] test_mcp_health_backend_mounted passed")
    test_mcp_rest_tools_catalog()
    print("[PASS] test_mcp_rest_tools_catalog passed")
    test_mcp_handshake_initialize()
    print("[PASS] test_mcp_handshake_initialize passed")
    test_mcp_protocol_tools_list()
    print("[PASS] test_mcp_protocol_tools_list passed")
    test_mcp_protocol_tools_call_weather()
    print("[PASS] test_mcp_protocol_tools_call_weather passed")
    test_mcp_direct_invoke_flood_classifier()
    print("[PASS] test_mcp_direct_invoke_flood_classifier passed")
    test_mcp_direct_invoke_dem_exposure()
    print("[PASS] test_mcp_direct_invoke_dem_exposure passed")
    test_mcp_direct_invoke_policy_rag()
    print("[PASS] test_mcp_direct_invoke_policy_rag passed")
    test_mcp_error_handling_unknown_method()
    print("[PASS] test_mcp_error_handling_unknown_method passed")
    print("\n>>> ALL 10 MCP END-TO-END TESTS PASSED 100%! <<<")
