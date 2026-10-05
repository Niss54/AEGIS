"""
AEGIS-CLIMATE — Agent 3 (Macro Transition & Financial Risk Engine) Test Suite
Validates ChromaDB RAG retrieval, multi-factor Value at Risk (VaR), bilingual civic dispatch, and MCP tool execution.
"""
import sys
import os
import time

sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.agent3_financial import financial_risk_engine
from mcp_hub.hub import app as mcp_app

backend_client = TestClient(app)
mcp_client = TestClient(mcp_app)


def test_chromadb_rag_query():
    """Verify ChromaDB regulatory policy vector query."""
    results = financial_risk_engine.rag.query("SEBI BRSR disclosure carbon penalty", top_k=2)
    assert len(results) >= 1
    titles = [r["metadata"].get("title", "") for r in results]
    assert any("SEBI BRSR" in t or "Carbon" in t for t in titles)
    print(f"[PASS] ChromaDB RAG retrieved {len(results)} clauses. Top title: {titles[0][:60]}...")


def test_financial_var_engine():
    """Verify multi-factor Value at Risk modeling."""
    res = financial_risk_engine.model_financial_var(
        location_label="Mumbai Mithi River Industrial Park",
        risk_score=0.88,
        waterlogging_depth_cm=85,
        buildings_at_risk=320,
        damage_estimate_inr=2_500_000_000,  # ₹250 Crores
        sector="Industrial Logistics"
    )
    assert res["status"] == "COMPLETED"
    assert res["var_estimate_inr"] > 2_500_000_000, "VaR must exceed direct physical loss"
    assert res["stranded_asset_risk"] == "HIGH"
    assert res["compliance_gap_pct"] >= 30
    assert len(res["recommended_actions"]) >= 3
    assert "business_interruption_loss_inr" in res["var_components"]
    assert res["var_components"]["estimated_downtime_days"] >= 10
    
    # Bilingual Alerts Check
    assert "आपातकालीन" in res["bilingual_alert_hindi"]
    assert "EXECUTIVE ALERT" in res["bilingual_alert_english"]
    print(f"[PASS] Financial VaR Engine: Total VaR=INR {res['var_estimate_inr']:,} ($ {res['var_estimate_usd']:,}), Stranded={res['stranded_asset_risk']}")


def test_tools_var_model_endpoint():
    """Test POST /api/v1/tools/var-model REST endpoint."""
    payload = {
        "location_name": "Bengaluru Outer Ring Road Corridor",
        "risk_score": 0.82,
        "waterlogging_depth_cm": 75,
        "buildings_at_risk": 210,
        "damage_estimate_inr": 1_800_000_000,
        "sector": "Tech & Financial Services"
    }
    res = backend_client.post("/api/v1/tools/var-model", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["COMPLETED", "success"]
    assert data["tool"] == "model_var_exposure"
    assert data["var_estimate_inr"] > 0
    print(f"[PASS] /api/v1/tools/var-model endpoint working: VaR=INR {data['var_estimate_inr']:,}")


def test_tools_policy_rag_endpoint():
    """Test POST /api/v1/tools/policy-rag REST endpoint."""
    res = backend_client.post("/api/v1/tools/policy-rag?query=NDMA%20stormwater%20flood%20barriers&top_k=2")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["tool"] == "query_policy_rag"
    assert data["results_count"] >= 1
    print(f"[PASS] /api/v1/tools/policy-rag endpoint working: Found {data['results_count']} policy clauses")


def test_events_financial_endpoint():
    """Test full workflow and GET /api/v1/events/{id}/financial."""
    analyze_res = backend_client.post("/api/v1/analyze", json={
        "lat": 19.0728,
        "lon": 72.8797,
        "location_name": "Mumbai Mithi River Basin",
        "simulated_additional_rain_mm": 90.0,
        "simulated_saturation_pct_override": 92.0
    })
    assert analyze_res.status_code == 200
    event_data = analyze_res.json()
    event_id = event_data["event_id"]

    res = backend_client.get(f"/api/v1/events/{event_id}/financial")
    assert res.status_code == 200
    fin_data = res.json()
    assert fin_data["status"] == "COMPLETED"
    assert fin_data["var_estimate_inr"] > 0
    assert fin_data["stranded_asset_risk"] in ["HIGH", "CRITICAL", "MEDIUM"]
    assert len(fin_data["applicable_regulations"]) > 0
    print(f"[PASS] /api/v1/events/{event_id}/financial endpoint retrieved executive VaR briefing")


def test_mcp_hub_query_policy_rag():
    """Test calling query_policy_rag through MCP Hub JSON-RPC 2.0."""
    rpc_payload = {
        "jsonrpc": "2.0",
        "method": "query_policy_rag",
        "params": {
            "query": "carbon tax and heavy emissions penalty framework",
            "damage_estimate_inr": 500000000
        },
        "id": "mcp-test-agent3"
    }
    res = mcp_client.post("/mcp/invoke", json=rpc_payload)
    assert res.status_code == 200
    resp_data = res.json()
    assert "result" in resp_data
    result = resp_data["result"]
    assert "applicable_regulations" in result
    print(f"[PASS] MCP Hub JSON-RPC dispatch: Tool returned {len(result['applicable_regulations'])} regulations")


if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING AGENT 3 (FINANCIAL VAR & RAG) TEST SUITE")
    print("=" * 60)
    test_chromadb_rag_query()
    test_financial_var_engine()
    test_tools_var_model_endpoint()
    test_tools_policy_rag_endpoint()
    test_events_financial_endpoint()
    test_mcp_hub_query_policy_rag()
    print("=" * 60)
    print(">>> ALL AGENT 3 FINANCIAL VAR & RAG TESTS PASSED (100%)! <<<")
    print("=" * 60)
