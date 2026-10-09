"""Disaster Bond Manager for AEGIS-CHAIN."""
from typing import Dict, Any, List, Optional
from backend.app.blockchain.chain_client import chain_client, AEGISChainClient


class DisasterBondManager:
    """Manages parametric disaster bonds, triggers, and payouts."""

    def __init__(self, client: Optional[AEGISChainClient] = None):
        self.client = client or chain_client

    async def list_bonds(self, lat: Optional[float] = None, lon: Optional[float] = None) -> List[Dict[str, Any]]:
        return self.client.get_bonds(lat, lon)

    async def notify_risk_event(self, lat: float, lon: float, risk_score_bps: int, assessment_id: str) -> Dict[str, Any]:
        return await self.client.notify_bond(lat, lon, risk_score_bps, assessment_id)


bond_manager = DisasterBondManager()
