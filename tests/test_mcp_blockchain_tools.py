"""Test suite for MCP Hub v2.0 Blockchain and IPFS tools."""
from fastapi.testclient import TestClient
from mcp_hub.hub import app

client = TestClient(app)


def test_mcp_v2_tools_list_contains_blockchain_tools():
    """Verify official MCP tools/list includes all 4 blockchain tools."""
    resp = client.post("/mcp/invoke", json={
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": "list-1"
    })
    assert resp.status_code == 200
    res = resp.json()["result"]
    tool_names = [t["name"] for t in res["tools"]]

    assert "fetch_weather_vectors" in tool_names
    assert "run_flood_classifier" in tool_names
    assert "compute_dem_exposure" in tool_names
    assert "query_policy_rag" in tool_names
    assert "anchor_risk_on_chain" in tool_names
    assert "store_on_ipfs" in tool_names
    assert "check_bond_trigger" in tool_names
    assert "check_cfmc_eligibility" in tool_names


def test_mcp_tools_call_anchor_risk_on_chain():
    """Verify MCP tools/call for anchor_risk_on_chain."""
    resp = client.post("/mcp/invoke", json={
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "anchor_risk_on_chain",
            "arguments": {
                "lat": 19.0728,
                "lon": 72.8797,
                "risk_score": 0.85,
                "ipfs_cid": "bafybeigdemo123",
                "location_name": "Mumbai Basin"
            }
        },
        "id": "call-anchor-1"
    })
    assert resp.status_code == 200
    data = resp.json()["result"]["data"]
    assert data["status"] == "anchored"
    assert "assessment_id" in data
    assert "tx_hash" in data
    assert "polygonscan.com" in data["explorer_url"]


def test_mcp_tools_call_store_on_ipfs():
    """Verify MCP tools/call for store_on_ipfs."""
    resp = client.post("/mcp/invoke", json={
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "store_on_ipfs",
            "arguments": {
                "payload": {"test": "data", "event": "mcp_test"}
            }
        },
        "id": "call-ipfs-1"
    })
    assert resp.status_code == 200
    data = resp.json()["result"]["data"]
    assert data["stored"] is True
    assert "cid" in data
    assert data["cid"].startswith("bafybeig")


def test_mcp_tools_call_check_bond_trigger():
    """Verify MCP tools/call for check_bond_trigger."""
    resp = client.post("/mcp/invoke", json={
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "check_bond_trigger",
            "arguments": {
                "lat": 19.0728,
                "lon": 72.8797,
                "risk_score_bps": 7800,
                "assessment_id": "0x12345"
            }
        },
        "id": "call-bond-1"
    })
    assert resp.status_code == 200
    data = resp.json()["result"]["data"]
    assert data["triggered"] is True
    assert data["bonds_checked"] >= 1


def test_mcp_tools_call_check_cfmc_eligibility():
    """Verify MCP tools/call for check_cfmc_eligibility."""
    resp = client.post("/mcp/invoke", json={
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "check_cfmc_eligibility",
            "arguments": {
                "risk_score": 0.88,
                "dem_depth_cm": 14.5
            }
        },
        "id": "call-cfmc-1"
    })
    assert resp.status_code == 200
    data = resp.json()["result"]["data"]
    assert data["eligible"] is True
    assert data["reward_amount"] == 100
    assert data["symbol"] == "CFMC"
