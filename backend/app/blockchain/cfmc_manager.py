"""Carbon Flood Mitigation Credit (CFMC) Manager for AEGIS-CHAIN."""
from typing import Dict, Any, Optional
from backend.app.blockchain.chain_client import chain_client, AEGISChainClient


class CFMCManager:
    """Manages CFMC token eligibility, minting, and retirement."""

    def __init__(self, client: Optional[AEGISChainClient] = None):
        self.client = client or chain_client

    async def check_and_mint_credit(
        self,
        beneficiary: str,
        assessment_id: str,
        lat: float,
        lon: float,
        risk_score_bps: int,
        dem_depth_cm: float
    ) -> Dict[str, Any]:
        return await self.client.issue_mitigation_credit(
            beneficiary=beneficiary,
            assessment_id=assessment_id,
            lat=lat,
            lon=lon,
            risk_score_bps=risk_score_bps,
            dem_depth_cm=dem_depth_cm
        )

    def get_balance(self, address: str) -> int:
        return self.client.get_cfmc_balance(address)


cfmc_manager = CFMCManager()
