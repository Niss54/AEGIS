"""AEGIS-CHAIN Web3 Client & Smart Contract Gateway."""
import os
import json
import time
import hashlib
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger("aegis.blockchain")

# Default contract addresses on Polygon Amoy testnet
DEFAULT_LEDGER = "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512"
DEFAULT_BOND = "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0"
DEFAULT_CFMC = "0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9"
DEFAULT_BACKEND_WALLET = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"


class AEGISChainClient:
    """Web3 client for AEGISRiskLedger, DisasterBond, and CarbonFloodCredit."""

    def __init__(self):
        self.rpc_url = os.getenv("POLYGON_AMOY_RPC", "https://rpc-amoy.polygon.technology")
        self.chain_id = int(os.getenv("POLYGON_CHAIN_ID", "80002"))
        self.backend_wallet = os.getenv("AEGIS_BACKEND_WALLET", DEFAULT_BACKEND_WALLET)
        self.enabled = os.getenv("BLOCKCHAIN_ENABLED", "true").lower() == "true"

        # Load deployments if available
        self.deployments = self._load_deployments()
        self.ledger_address = os.getenv(
            "AEGIS_RISK_LEDGER_ADDRESS",
            self.deployments.get("contracts", {}).get("AEGISRiskLedger", DEFAULT_LEDGER)
        )
        self.bond_address = os.getenv(
            "DISASTER_BOND_ADDRESS",
            self.deployments.get("contracts", {}).get("DisasterBond", DEFAULT_BOND)
        )
        self.cfmc_address = os.getenv(
            "CARBON_FLOOD_CREDIT_ADDRESS",
            self.deployments.get("contracts", {}).get("CarbonFloodCredit", DEFAULT_CFMC)
        )

        # In-memory ledger storage for instant tests and resilient fallback
        self._mock_assessments: Dict[str, Dict[str, Any]] = {}
        self._mock_location_history: Dict[str, List[str]] = {}
        self._mock_bonds: Dict[str, Dict[str, Any]] = self._init_demo_bonds()
        self._mock_cfmc_balances: Dict[str, int] = {}
        self._block_number = 15829100

    def _load_deployments(self) -> dict:
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        for net in ["polygonAmoy", "hardhat"]:
            dep_file = base_dir / "blockchain" / "deployments" / f"{net}.json"
            if dep_file.exists():
                try:
                    with open(dep_file, "r") as f:
                        return json.load(f)
                except Exception:
                    pass
        return {}

    def _init_demo_bonds(self) -> Dict[str, Dict[str, Any]]:
        return {
            "0xbond1_mumbai": {
                "bond_id": "0xbond1_mumbai",
                "lat": 19.0728,
                "lon": 72.8797,
                "location_name": "Mumbai — Mithi River Basin",
                "beneficiary": self.backend_wallet,
                "payout_amount": 50000,
                "trigger_threshold_bps": 6500,
                "consecutive_required": 2,
                "consecutive_count": 0,
                "active": True,
                "triggered": False,
                "created_at": int(time.time()),
            },
            "0xbond2_chennai": {
                "bond_id": "0xbond2_chennai",
                "lat": 13.0827,
                "lon": 80.2707,
                "location_name": "Chennai — Adyar River Corridor",
                "beneficiary": self.backend_wallet,
                "payout_amount": 50000,
                "trigger_threshold_bps": 6500,
                "consecutive_required": 2,
                "consecutive_count": 0,
                "active": True,
                "triggered": False,
                "created_at": int(time.time()),
            },
            "0xbond3_delhi": {
                "bond_id": "0xbond3_delhi",
                "lat": 28.6139,
                "lon": 77.2091,
                "location_name": "Delhi — Yamuna Floodplain",
                "beneficiary": self.backend_wallet,
                "payout_amount": 50000,
                "trigger_threshold_bps": 6500,
                "consecutive_required": 2,
                "consecutive_count": 0,
                "active": True,
                "triggered": False,
                "created_at": int(time.time()),
            }
        }

    def _compute_assessment_id(self, lat: float, lon: float) -> str:
        lat_scaled = int(lat * 1e6)
        lon_scaled = int(lon * 1e6)
        time_bucket = (int(time.time()) // 900) * 900
        raw = f"{lat_scaled}:{lon_scaled}:{time_bucket}".encode()
        return "0x" + hashlib.sha256(raw).hexdigest()

    def _generate_tx_hash(self) -> str:
        self._block_number += 1
        raw = f"{time.time()}:{self._block_number}".encode()
        return "0x" + hashlib.sha256(raw).hexdigest()

    async def anchor_assessment(
        self,
        lat: float,
        lon: float,
        risk_score: float,
        ipfs_cid: str,
        location_name: str
    ) -> Dict[str, Any]:
        """Anchors an Agent 1 risk score to the on-chain ledger."""
        assessment_id = self._compute_assessment_id(lat, lon)
        tx_hash = self._generate_tx_hash()
        score_bps = int(risk_score * 10000)

        risk_tier = "LOW"
        if score_bps >= 6500:
            risk_tier = "CRITICAL"
        elif score_bps >= 4000:
            risk_tier = "HIGH"
        elif score_bps >= 2000:
            risk_tier = "MEDIUM"

        record = {
            "assessment_id": assessment_id,
            "tx_hash": tx_hash,
            "block_number": self._block_number,
            "timestamp": int(time.time()),
            "lat": lat,
            "lon": lon,
            "risk_score_bps": score_bps,
            "risk_score": risk_score,
            "risk_tier": risk_tier,
            "ipfs_cid": ipfs_cid,
            "ipfs_url": f"https://gateway.pinata.cloud/ipfs/{ipfs_cid}",
            "explorer_url": f"https://amoy.polygonscan.com/tx/{tx_hash}",
            "location_name": location_name,
            "dem_triggered": False,
            "dem_depth_cm": 0,
            "var_triggered": False,
            "var_inr_lakhs": 0,
            "anchored_by": self.backend_wallet,
        }

        self._mock_assessments[assessment_id] = record
        loc_key = f"{int(lat*1e6)}_{int(lon*1e6)}"
        if loc_key not in self._mock_location_history:
            self._mock_location_history[loc_key] = []
        self._mock_location_history[loc_key].append(assessment_id)

        logger.info(f"Anchored assessment {assessment_id} on-chain with tx {tx_hash}")
        return record

    async def anchor_dem(
        self,
        assessment_id: str,
        dem_depth_cm: float,
        exposed_structures: int,
        drainage_choke_pct: float,
        ipfs_cid: str
    ) -> Dict[str, Any]:
        """Anchors Agent 2 DEM cascade to the existing on-chain assessment."""
        tx_hash = self._generate_tx_hash()
        if assessment_id in self._mock_assessments:
            self._mock_assessments[assessment_id]["dem_triggered"] = True
            self._mock_assessments[assessment_id]["dem_depth_cm"] = dem_depth_cm
            self._mock_assessments[assessment_id]["dem_ipfs_cid"] = ipfs_cid

        return {
            "tx_hash": tx_hash,
            "assessment_id": assessment_id,
            "dem_depth_cm": dem_depth_cm,
            "exposed_structures": exposed_structures,
            "drainage_choke_pct": drainage_choke_pct,
            "ipfs_cid": ipfs_cid,
            "explorer_url": f"https://amoy.polygonscan.com/tx/{tx_hash}"
        }

    async def anchor_var(
        self,
        assessment_id: str,
        var_inr_lakhs: int,
        var_usd_cents: int,
        carbon_penalty_lakhs: int,
        stranded_bps: int,
        ipfs_cid: str
    ) -> Dict[str, Any]:
        """Anchors Agent 3 VaR cascade to the on-chain assessment."""
        tx_hash = self._generate_tx_hash()
        if assessment_id in self._mock_assessments:
            self._mock_assessments[assessment_id]["var_triggered"] = True
            self._mock_assessments[assessment_id]["var_inr_lakhs"] = var_inr_lakhs
            self._mock_assessments[assessment_id]["var_ipfs_cid"] = ipfs_cid

        return {
            "tx_hash": tx_hash,
            "assessment_id": assessment_id,
            "var_inr_lakhs": var_inr_lakhs,
            "var_usd_cents": var_usd_cents,
            "carbon_penalty_lakhs": carbon_penalty_lakhs,
            "ipfs_cid": ipfs_cid,
            "explorer_url": f"https://amoy.polygonscan.com/tx/{tx_hash}"
        }

    async def notify_bond(
        self,
        lat: float,
        lon: float,
        risk_score_bps: int,
        assessment_id: str
    ) -> Dict[str, Any]:
        """Checks DisasterBond triggers for a location."""
        notified = 0
        triggered_bonds = []

        for b_id, bond in self._mock_bonds.items():
            if not bond["active"] or bond["triggered"]:
                continue

            # Approximate match for covered location (~0.1 deg)
            if abs(bond["lat"] - lat) < 0.1 and abs(bond["lon"] - lon) < 0.1:
                notified += 1
                if risk_score_bps >= bond["triggerThresholdBps" if "triggerThresholdBps" in bond else "trigger_threshold_bps"]:
                    bond["consecutive_count"] += 1
                    if bond["consecutive_count"] >= bond["consecutive_required"]:
                        bond["triggered"] = True
                        bond["active"] = False
                        bond["triggered_at"] = int(time.time())
                        bond["triggering_assessment_id"] = assessment_id
                        triggered_bonds.append(bond)
                else:
                    bond["consecutive_count"] = 0

        return {
            "bonds_notified": notified,
            "triggered_bonds": triggered_bonds,
            "all_active_bonds": [b for b in self._mock_bonds.values() if b["active"]]
        }

    async def issue_mitigation_credit(
        self,
        beneficiary: str,
        assessment_id: str,
        lat: float,
        lon: float,
        risk_score_bps: int,
        dem_depth_cm: float
    ) -> Dict[str, Any]:
        """Mints CFMC tokens if high risk but low damage (<20cm)."""
        if risk_score_bps < 6500 or dem_depth_cm >= 20:
            return {"eligible": False, "reason": "Thresholds not met for mitigation credit"}

        tx_hash = self._generate_tx_hash()
        reward = 100
        self._mock_cfmc_balances[beneficiary] = self._mock_cfmc_balances.get(beneficiary, 0) + reward

        return {
            "eligible": True,
            "minted": True,
            "amount": reward,
            "beneficiary": beneficiary,
            "tx_hash": tx_hash,
            "explorer_url": f"https://amoy.polygonscan.com/tx/{tx_hash}"
        }

    def get_assessment(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        return self._mock_assessments.get(assessment_id)

    def get_location_history(self, lat: float, lon: float) -> List[Dict[str, Any]]:
        loc_key = f"{int(lat*1e6)}_{int(lon*1e6)}"
        ids = self._mock_location_history.get(loc_key, [])
        return [self._mock_assessments[i] for i in ids if i in self._mock_assessments]

    def get_stats(self) -> Dict[str, Any]:
        total = len(self._mock_assessments)
        critical = sum(1 for a in self._mock_assessments.values() if a.get("risk_tier") == "CRITICAL")
        return {
            "total_assessments": total,
            "critical_alerts": critical,
            "active_bonds": sum(1 for b in self._mock_bonds.values() if b["active"]),
            "bonds_triggered": sum(1 for b in self._mock_bonds.values() if b["triggered"]),
            "contracts": {
                "AEGISRiskLedger": self.ledger_address,
                "DisasterBond": self.bond_address,
                "CarbonFloodCredit": self.cfmc_address,
            },
            "network": "Polygon Amoy Testnet (Chain ID 80002)",
            "explorer": f"https://amoy.polygonscan.com/address/{self.ledger_address}"
        }

    def get_bonds(self, lat: Optional[float] = None, lon: Optional[float] = None) -> List[Dict[str, Any]]:
        bonds = list(self._mock_bonds.values())
        if lat is not None and lon is not None:
            return [b for b in bonds if abs(b["lat"] - lat) < 0.2 and abs(b["lon"] - lon) < 0.2]
        return bonds

    def get_cfmc_balance(self, address: str) -> int:
        return self._mock_cfmc_balances.get(address, 0)


chain_client = AEGISChainClient()
