"""Integration tests for AEGIS-CHAIN v2.0 blockchain layer and evidence verifier."""
import pytest
import time
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.blockchain.chain_client import AEGISChainClient, chain_client
from backend.app.blockchain.risk_anchor import RiskAnchorService
from backend.app.blockchain.evidence_verifier import evidence_verifier

client = TestClient(app)


class TestRiskAnchorService:
    @pytest.fixture
    def mock_chain_client(self):
        client_mock = AsyncMock(spec=AEGISChainClient)
        client_mock.anchor_assessment.return_value = {
            "tx_hash": "0xabc123456789",
            "assessment_id": "0xdeadbeef12345678",
            "block_number": 12345678,
            "status": "pending"
        }
        return client_mock

    @pytest.mark.asyncio
    async def test_anchor_does_not_block_analysis(self, mock_chain_client):
        """Blockchain anchoring must be non-blocking (<0.1s response)."""
        service = RiskAnchorService(client=mock_chain_client)
        start = time.time()
        res = await service.anchor_non_blocking(
            lat=19.0728,
            lon=72.8797,
            risk_score=0.78,
            ipfs_cid="bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi",
            location_name="Mumbai"
        )
        elapsed = time.time() - start
        assert elapsed < 0.1, "Blockchain anchoring must not block the analysis"
        assert res["status"] == "anchoring_initiated"

    @pytest.mark.asyncio
    async def test_anchor_failure_does_not_crash_system(self, mock_chain_client):
        """System must continue gracefully if blockchain RPC is unavailable."""
        mock_chain_client.anchor_assessment.side_effect = Exception("RPC timeout")
        service = RiskAnchorService(client=mock_chain_client)

        # Should not raise exception
        res = await service.anchor_non_blocking(
            lat=19.0728,
            lon=72.8797,
            risk_score=0.78,
            ipfs_cid="bafybei...",
            location_name="Mumbai"
        )
        assert res["status"] == "anchoring_initiated"

    @pytest.mark.asyncio
    async def test_bond_trigger_notification(self, mock_chain_client):
        """DisasterBond.notifyAssessment is called for CRITICAL assessments."""
        mock_chain_client.notify_bond.return_value = {"bonds_notified": 1}
        service = RiskAnchorService(client=mock_chain_client)
        res = await service.process_critical_alert(
            lat=19.0728,
            lon=72.8797,
            risk_score_bps=7800,
            assessment_id="0xdeadbeef..."
        )
        mock_chain_client.notify_bond.assert_awaited_once()
        assert res["bonds_notified"] == 1


class TestBlockchainEndpoints:
    def test_blockchain_status_endpoint(self):
        """Verify GET /api/v2/blockchain/status returns chain metadata."""
        resp = client.get("/api/v2/blockchain/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "network" in data
        assert "contracts" in data
        assert "AEGISRiskLedger" in data["contracts"]
        assert "DisasterBond" in data["contracts"]
        assert "CarbonFloodCredit" in data["contracts"]

    def test_blockchain_anchor_and_retrieve(self):
        """Verify manual anchor and on-chain retrieval."""
        payload = {
            "lat": 19.0728,
            "lon": 72.8797,
            "risk_score": 0.85,
            "ipfs_cid": "bafybeigdemo12345678",
            "location_name": "Mumbai Basin Test"
        }
        res_anchor = client.post("/api/v2/blockchain/anchor", json=payload)
        assert res_anchor.status_code == 200
        data = res_anchor.json()
        assert "assessment_id" in data
        assert "tx_hash" in data
        assessment_id = data["assessment_id"]

        # Fetch assessment
        res_get = client.get(f"/api/v2/blockchain/assessment/{assessment_id}")
        assert res_get.status_code == 200
        ass_data = res_get.json()
        assert ass_data["assessment_id"] == assessment_id
        assert ass_data["risk_tier"] == "CRITICAL"

    def test_disaster_bonds_list(self):
        """Verify parametric disaster bonds listing."""
        resp = client.get("/api/v2/blockchain/bonds")
        assert resp.status_code == 200
        bonds = resp.json()["bonds"]
        assert len(bonds) >= 3
        mumbai_bond = next((b for b in bonds if "Mumbai" in b["location_name"]), None)
        assert mumbai_bond is not None
        assert mumbai_bond["active"] is True

    def test_cfmc_token_balance_and_retire(self):
        """Verify CFMC balance read and token retirement."""
        addr = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        res_bal = client.get(f"/api/v2/blockchain/cfmc/balance?address={addr}")
        assert res_bal.status_code == 200
        assert res_bal.json()["symbol"] == "CFMC"

        res_retire = client.post("/api/v2/blockchain/cfmc/retire", json={
            "amount": 20,
            "reason": "Scope 1 Inundation Carbon Offset"
        })
        assert res_retire.status_code == 200
        assert res_retire.json()["status"] == "retired"


class TestEvidenceVerificationAndTamperDetection:
    def test_evidence_tamper_detection_pass(self):
        """Valid report data must PASS verification against its cryptographic digest."""
        report = {
            "lat": 19.0728,
            "lon": 72.8797,
            "location_name": "Mumbai Logistics Hub",
            "risk_score": 0.82,
            "risk_tier": "CRITICAL",
            "waterlogging_depth_cm": 75,
            "var_estimate_inr": 250000000
        }
        sha_digest, _ = evidence_verifier.compute_digests(report)

        verif_res = evidence_verifier.verify(report, sha_digest)
        assert verif_res["status"] == "PASS"
        assert verif_res["verified"] is True
        assert verif_res["tampered"] is False

    def test_evidence_tamper_detection_fail(self):
        """Altered report data must FAIL verification and flag TAMPER DETECTED."""
        original_report = {
            "lat": 19.0728,
            "lon": 72.8797,
            "location_name": "Mumbai Logistics Hub",
            "risk_score": 0.82,
            "risk_tier": "CRITICAL",
            "waterlogging_depth_cm": 75,
            "var_estimate_inr": 250000000
        }
        sha_digest, _ = evidence_verifier.compute_digests(original_report)

        # Alter single field: downplay risk from 0.82 to 0.20
        tampered_report = dict(original_report)
        tampered_report["risk_score"] = 0.20

        verif_res = evidence_verifier.verify(tampered_report, sha_digest)
        assert verif_res["status"] == "FAIL"
        assert verif_res["verified"] is False
        assert verif_res["tampered"] is True
        assert "TAMPER DETECTED" in verif_res["message"]

    def test_v2_analyze_pipeline_with_chain(self):
        """Verify POST /api/v2/analyze executes multi-agent cascade and on-chain anchoring."""
        res = client.post("/api/v2/analyze", json={
            "lat": 19.0728,
            "lon": 72.8797,
            "location_name": "Mumbai — Mithi River & Kurla Basin",
            "simulated_additional_rain_mm": 105.0,
            "simulated_saturation_pct_override": 90.0
        })
        assert res.status_code == 200
        data = res.json()

        # Check multi-agent outputs
        assert data["agent1"]["risk_score"] > 0.65
        assert data["agent2"] is not None
        assert data["agent3"] is not None

        # Check v2 blockchain metadata
        assert "blockchain" in data
        bc = data["blockchain"]
        assert bc["version"] == "v2.0.0"
        assert "tx_hash" in bc
        assert "assessment_id" in bc
        assert "ipfs_cid" in bc
        assert "evidence_digest" in bc
        assert bc["bond_status"]["notified"] is True
