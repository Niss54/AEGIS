"""
Phase 14 Comprehensive Verification Suite
Module: tests.test_phase14_contract_ledger
Governance: Gravitas Reliability Runtime · Model Context Protocol Compliant

Mathematical Governing Equation:
Hash_onchain = keccak256(Hotspot || VaR || IPFS_CID)

Verifies:
1. PRD Phase 14 Execution Invariant & BlockchainAnchorModel schema adherence
2. Deterministic Keccak256 mathematical invariant calculation and 32-byte bounds
3. Circuit breaker failure recovery protocol (CLOSED -> OPEN -> HALF_OPEN -> CLOSED)
4. Local in-memory Tier 2 ledger fallback & IPFS synthetic CID generation
5. On-chain risk anchor creation and verification
6. FastAPI REST endpoints (/blockchain/phase14/pipeline, /hash/compute, /health)
7. MCP Hub JSON-RPC 2.0 tool execution (compute_onchain_keccak_hash, anchor_assessment_to_ledger, verify_onchain_anchor)
"""
import time
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.contract_ledger import (
    ContractLedgerController,
    BlockchainAnchorModel,
    compute_keccak256_hash
)

client = TestClient(app)


# -----------------------------------------------------------------------------
# 1. PRD Execution Invariant Test (as specified in PRD.md Section 6)
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_phase_14_execution_invariant():
    """
    Direct invariant verification specified in PRD.md Section 6.
    Ensures BlockchainAnchorModel schema validity, operational status, and cryptographic flag.
    """
    controller = ContractLedgerController()
    sample_payload = {"event_id": "TEST-PHASE-14", "telemetry": 42.0}
    result = await controller.execute_phase_pipeline(sample_payload)

    assert result.event_id == "TEST-PHASE-14"
    assert result.verified_flag is True
    assert result.metadata["status"] == "OPERATIONAL"
    assert result.metadata["phase_id"] == 14
    assert result.metadata["governing_equation"] == "Hash_onchain = keccak256(Hotspot || VaR || IPFS_CID)"
    assert "onchain_hash" in result.metadata
    assert result.execution_tier == "ENTERPRISE_PROD"


# -----------------------------------------------------------------------------
# 2. Mathematical Governing Invariant Test
# -----------------------------------------------------------------------------
def test_keccak256_mathematical_governing_equation():
    """
    Tests: Hash_onchain = keccak256(Hotspot || VaR || IPFS_CID)
    Confirms:
    1. Deterministic output: same input produces identical 32-byte hash.
    2. Strict sensitivity: altering any variable produces a completely different hash.
    3. Proper 32-byte hex formatting (0x + 64 characters = 66 characters).
    """
    hotspot1 = "Mumbai Mithi River Basin"
    var1 = 350.50
    cid1 = "bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi"

    hash_a = compute_keccak256_hash(hotspot1, var1, cid1)
    hash_b = compute_keccak256_hash(hotspot1, var1, cid1)

    # Determinism
    assert hash_a == hash_b
    assert hash_a.startswith("0x")
    assert len(hash_a) == 66  # 0x + 64 hex characters (32 bytes)

    # Sensitivity: change VaR by 0.01
    hash_var_diff = compute_keccak256_hash(hotspot1, 350.51, cid1)
    assert hash_a != hash_var_diff

    # Sensitivity: change Hotspot
    hash_hotspot_diff = compute_keccak256_hash("Chennai Adyar River Corridor", var1, cid1)
    assert hash_a != hash_hotspot_diff

    # Sensitivity: change CID
    hash_cid_diff = compute_keccak256_hash(hotspot1, var1, "bafybeighacked_cid_attempt")
    assert hash_a != hash_cid_diff


def test_keccak256_solidity_data_types_and_encoding():
    """
    Verifies precise Solidity EVM encoding and data types:
    - Hotspot: string
    - VaR: uint256 (scaled by 1e4, basis points precision)
    - IPFS_CID: string
    - Canonical abi.encode vs gas-optimized abi.encodePacked
    """
    hotspot = "Mumbai Mithi River Basin"
    var_amount = 250.0
    ipfs_cid = "bafybeigterra_sentinel_phase14_mock_cid_v1"

    details = ContractLedgerController().get_onchain_hash_details(hotspot, var_amount, ipfs_cid)
    assert details["var_scaled"] == 2500000  # 250.0 * 10000
    assert details["precision_scale"] == 10000
    assert details["data_types"]["hotspot"] == "string"
    assert "uint256" in details["data_types"]["var_scaled"]
    assert details["data_types"]["ipfs_cid"] == "string"
    assert details["onchain_hash"].startswith("0x")
    assert details["onchain_hash_packed"].startswith("0x")
    assert len(details["onchain_hash"]) == 66
    assert len(details["onchain_hash_packed"]) == 66


# -----------------------------------------------------------------------------
# 3. Circuit Breaker State Transitions & Recovery
# -----------------------------------------------------------------------------
def test_contract_ledger_circuit_breaker():
    """
    Verifies Circuit Breaker Protocol (PRD Section 7):
    1. Error rate >= 3 consecutive failures -> Circuit OPEN.
    2. Requests route to Tier 2 local fallback ledger.
    3. Cooldown probe (30s) -> HALF_OPEN.
    4. Successful probe -> CLOSED.
    """
    controller = ContractLedgerController()
    controller.circuit_state = "CLOSED"
    controller.consecutive_failures = 0

    err = ConnectionError("Simulated RPC Polygon Amoy Timeout")

    # Failure 1
    controller._record_failure(err)
    assert controller.circuit_state == "CLOSED"
    assert controller.consecutive_failures == 1

    # Failure 2
    controller._record_failure(err)
    assert controller.circuit_state == "CLOSED"
    assert controller.consecutive_failures == 2

    # Failure 3 -> Trips to OPEN
    controller._record_failure(err)
    assert controller.circuit_state == "OPEN"
    assert controller.consecutive_failures == 3
    assert controller.metrics["circuit_trips"] >= 1

    # Cooldown simulation
    controller.last_state_change = time.time() - 35.0  # 35 seconds elapsed > 30s cooldown
    controller._check_circuit_cooldown()
    assert controller.circuit_state == "HALF_OPEN"

    # Successful recovery probe
    controller._record_success()
    assert controller.circuit_state == "CLOSED"
    assert controller.consecutive_failures == 0


# -----------------------------------------------------------------------------
# 4. On-Chain Ledger & Fallback Storage Lifecycle
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_ledger_anchor_and_verification_lifecycle():
    """
    Tests complete anchoring and verification lifecycle:
    1. Anchor assessment with Keccak256 hash
    2. Verify anchor in ledger
    3. Ensure cryptographic integrity
    """
    controller = ContractLedgerController()
    hotspot = "Bengaluru Bellandur Catchment"
    var_amount = 180.75
    cid = "bafybeigbellandur_test_cid_2026"

    anchor = await controller.anchor_risk_assessment(
        hotspot=hotspot,
        var_amount=var_amount,
        ipfs_cid=cid,
        risk_score=0.82,
        lat=12.9352,
        lon=77.6740,
        dem_depth_cm=65.0
    )

    assessment_id = anchor["assessment_id"]
    assert assessment_id.startswith("0x")
    assert anchor["verified"] is True
    assert anchor["hotspot"] == hotspot

    # Verify anchor exists
    verification = controller.verify_assessment(assessment_id)
    assert verification["verified"] is True
    assert verification["assessment_id"] == assessment_id
    assert verification["record"]["var_amount"] == var_amount

    # Verify non-existent anchor returns verified=False
    non_existent = controller.verify_assessment("0x0000000000000000000000000000000000000000000000000000000000000000")
    assert non_existent["verified"] is False


# -----------------------------------------------------------------------------
# 5. FastAPI REST API Endpoints
# -----------------------------------------------------------------------------
def test_fastapi_blockchain_phase14_endpoints():
    """
    Tests REST endpoints:
    - POST /api/v2/blockchain/hash/compute
    - GET /api/v2/blockchain/phase14/health
    - POST /api/v2/blockchain/phase14/pipeline
    - GET /api/v2/blockchain/status
    """
    # 1. Compute Keccak hash
    r_hash = client.post("/api/v2/blockchain/hash/compute", json={
        "hotspot": "Delhi Yamuna Floodplain",
        "var_amount": 420.0,
        "ipfs_cid": "bafybeigdelhi_yamuna_cid"
    })
    assert r_hash.status_code == 200
    h_data = r_hash.json()
    assert h_data["onchain_hash"].startswith("0x")
    assert h_data["governing_equation"] == "Hash_onchain = keccak256(Hotspot || VaR || IPFS_CID)"

    # 2. Health
    r_health = client.get("/api/v2/blockchain/phase14/health")
    assert r_health.status_code == 200
    health_data = r_health.json()
    assert health_data["status"] == "OPERATIONAL"
    assert "circuit_state" in health_data
    assert "contracts" in health_data

    # 3. Pipeline
    r_pipe = client.post("/api/v2/blockchain/phase14/pipeline", json={
        "event_id": "REST-EVT-P14",
        "hotspot": "Assam Brahmaputra Basin",
        "var_amount": 550.0,
        "risk_score": 0.89
    })
    assert r_pipe.status_code == 200
    pipe_data = r_pipe.json()
    assert pipe_data["event_id"] == "REST-EVT-P14"
    assert pipe_data["verified_flag"] is True
    assert pipe_data["execution_tier"] == "ENTERPRISE_PROD"
    assert pipe_data["metadata"]["onchain_hash"].startswith("0x")

    # 4. Chain Status
    r_status = client.get("/api/v2/blockchain/status")
    assert r_status.status_code == 200
    status_data = r_status.json()
    assert "contracts" in status_data
    assert "AEGISRiskLedger" in status_data["contracts"]


# -----------------------------------------------------------------------------
# 6. MCP Hub Tools Invocation (Phase 14 Tools)
# -----------------------------------------------------------------------------
def test_mcp_hub_phase14_tools():
    """
    Verifies JSON-RPC 2.0 tool execution via MCP Hub:
    - compute_onchain_keccak_hash
    - anchor_assessment_to_ledger
    - verify_onchain_anchor
    """
    # 1. compute_onchain_keccak_hash
    rpc_hash = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "compute_onchain_keccak_hash",
            "arguments": {
                "hotspot": "Mundra Coastal Corridor",
                "var_amount": 310.0,
                "ipfs_cid": "bafybeigmundra_cid_test"
            }
        },
        "id": "mcp-p14-1"
    }
    r1 = client.post("/mcp/invoke", json=rpc_hash)
    assert r1.status_code == 200
    res1 = r1.json()["result"]["data"]
    assert res1["onchain_hash"].startswith("0x")
    assert res1["hotspot"] == "Mundra Coastal Corridor"
    expected_hash = res1["onchain_hash"]

    # 2. anchor_assessment_to_ledger
    rpc_anchor = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "anchor_assessment_to_ledger",
            "arguments": {
                "hotspot": "Mundra Coastal Corridor",
                "var_amount": 310.0,
                "ipfs_cid": "bafybeigmundra_cid_test",
                "risk_score": 0.74,
                "lat": 22.8396,
                "lon": 69.7258
            }
        },
        "id": "mcp-p14-2"
    }
    r2 = client.post("/mcp/invoke", json=rpc_anchor)
    assert r2.status_code == 200
    res2 = r2.json()["result"]["data"]
    assert res2["onchain_hash"] == expected_hash
    assert res2["verified"] is True

    # 3. verify_onchain_anchor
    rpc_verify = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "verify_onchain_anchor",
            "arguments": {
                "assessment_id": expected_hash
            }
        },
        "id": "mcp-p14-3"
    }
    r3 = client.post("/mcp/invoke", json=rpc_verify)
    assert r3.status_code == 200
    res3 = r3.json()["result"]["data"]
    assert res3["verified"] is True
    assert res3["assessment_id"] == expected_hash
