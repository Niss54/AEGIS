"""
AEGIS-CLIMATE — Phase 4: Autonomous Stablecoin Settlement & Micro-Disaster Bond Liquidity Layer Test Suite
Validates:
1. Programmatic USDC emergency relief settlement for AI agents
2. UNDP Double-Counting Defense (duplicate digest prevention)
3. Parametric flood depth thresholding (min 50cm)
4. Programmatic carbon offset retirement (CarbonFloodCredit / Toucan Protocol)
5. REST API endpoints & blockchain stats telemetry
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.blockchain.chain_client import chain_client

client = TestClient(app)


def test_chain_client_stats_includes_settlement_pool():
    """Verify blockchain stats include AgenticSettlementPool contract and telemetry."""
    stats = chain_client.get_stats()
    assert "contracts" in stats
    assert "AgenticSettlementPool" in stats["contracts"]
    assert "ClimateEvidenceRegistry" in stats["contracts"]
    assert "settlement_events" in stats
    assert "total_settled_usdc" in stats


def test_chain_client_settle_relief_success():
    """Verify successful programmatic stablecoin settlement."""
    digest = "0x" + "a" * 64
    beneficiary = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    depth_cm = 75

    res = chain_client.settle_emergency_relief(
        evidence_digest=digest,
        depth_cm=depth_cm,
        municipal_beneficiary=beneficiary,
        zk_proof="0x1234"
    )

    assert res["status"] == "SETTLED"
    assert res["evidence_digest"] == digest
    assert res["municipal_beneficiary"] == beneficiary
    assert res["payout_amount_usdc"] == 50000
    assert res["flood_depth_cm"] == 75
    assert res["undp_double_counting_prevented"] is True
    assert res["zk_proof_verified"] is True
    assert res["tx_hash"].startswith("0x")
    assert chain_client.is_relief_settled(digest) is True


def test_chain_client_undp_double_counting_prevention():
    """Verify that re-settling the same evidence digest raises an error (UNDP defense)."""
    digest = "0x" + "b" * 64
    beneficiary = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"

    # First settlement succeeds
    chain_client.settle_emergency_relief(digest, 80, beneficiary)

    # Second settlement MUST be rejected
    with pytest.raises(ValueError, match="UNDP Double-Counting Defense"):
        chain_client.settle_emergency_relief(digest, 80, beneficiary)


def test_chain_client_depth_threshold_rejection():
    """Verify rejection when flood depth is below 50cm trigger threshold."""
    digest = "0x" + "c" * 64
    beneficiary = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"

    with pytest.raises(ValueError, match="below the 50cm trigger threshold"):
        chain_client.settle_emergency_relief(digest, 30, beneficiary)


def test_chain_client_retire_offset_resilience():
    """Verify programmatic carbon offset retirement tied to flood resilience evidence."""
    digest = "0x" + "d" * 64
    memo = "Toucan / KlimaDAO programmatic offset retirement for Gomti Basin flood wall"

    res = chain_client.retire_offset_for_flood_resilience(
        amount=100,
        evidence_digest=digest,
        memo=memo
    )

    assert res["status"] == "RETIRED"
    assert res["amount_cfmc"] == 100
    assert res["evidence_digest"] == digest
    assert res["memo"] == memo
    assert res["tx_hash"].startswith("0x")


def test_rest_api_settle_relief_endpoint():
    """Test POST /api/v2/blockchain/settle-relief REST endpoint."""
    digest = "0x" + "e" * 64
    payload = {
        "evidence_digest": digest,
        "flood_depth_cm": 68,
        "municipal_beneficiary": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "zk_proof": "0x5678"
    }

    res = client.post("/api/v2/blockchain/settle-relief", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SETTLED"
    assert data["payout_amount_usdc"] == 50000

    # Repeat call must fail with 400 (UNDP double-counting defense)
    res_repeat = client.post("/api/v2/blockchain/settle-relief", json=payload)
    assert res_repeat.status_code == 400
    assert "UNDP Double-Counting Defense" in res_repeat.json()["detail"]


def test_rest_api_retire_offset_resilience_endpoint():
    """Test POST /api/v2/blockchain/cfmc/retire-resilience REST endpoint."""
    payload = {
        "amount": 75,
        "evidence_digest": "0x" + "f" * 64,
        "memo": "KlimaDAO retirement for Orange County Newport coastal barrier"
    }
    res = client.post("/api/v2/blockchain/cfmc/retire-resilience", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "RETIRED"
    assert data["amount_cfmc"] == 75
