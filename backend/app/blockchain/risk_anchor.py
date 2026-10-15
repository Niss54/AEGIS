"""Risk Anchor Service for non-blocking on-chain transaction lifecycle."""
import asyncio
import logging
from typing import Dict, Any, Optional
from backend.app.blockchain.chain_client import chain_client, AEGISChainClient

logger = logging.getLogger("aegis.risk_anchor")


class RiskAnchorService:
    """Manages asynchronous, non-blocking on-chain risk anchoring."""

    def __init__(self, client: Optional[AEGISChainClient] = None):
        self.client = client or chain_client
        self.retry_queue: asyncio.Queue = asyncio.Queue()
        self._bg_tasks = set()

    async def anchor_non_blocking(
        self,
        lat: float,
        lon: float,
        risk_score: float,
        ipfs_cid: str,
        location_name: str
    ) -> Dict[str, Any]:
        """Fire-and-forget non-blocking anchoring. Returns immediate pending ticket."""
        task = asyncio.create_task(
            self._anchor_worker(lat, lon, risk_score, ipfs_cid, location_name)
        )
        self._bg_tasks.add(task)
        task.add_done_callback(self._bg_tasks.discard)

        # Immediate ticket returned in < 1ms
        return {
            "status": "anchoring_initiated",
            "lat": lat,
            "lon": lon,
            "risk_score": risk_score,
            "ipfs_cid": ipfs_cid,
            "location_name": location_name,
        }

    async def _anchor_worker(
        self,
        lat: float,
        lon: float,
        risk_score: float,
        ipfs_cid: str,
        location_name: str
    ):
        try:
            res = await self.client.anchor_assessment(
                lat=lat,
                lon=lon,
                risk_score=risk_score,
                ipfs_cid=ipfs_cid,
                location_name=location_name
            )
            assessment_id = res.get("assessment_id")
            score_bps = int(risk_score * 10000)
            if score_bps >= 6500 and assessment_id:
                await self.process_critical_alert(lat, lon, score_bps, assessment_id)
        except Exception as e:
            logger.error(f"Anchor failed, placing into retry queue: {e}")
            await self.retry_queue.put({
                "lat": lat,
                "lon": lon,
                "risk_score": risk_score,
                "ipfs_cid": ipfs_cid,
                "location_name": location_name
            })

    async def process_critical_alert(
        self,
        lat: float,
        lon: float,
        risk_score_bps: int,
        assessment_id: str
    ) -> Dict[str, Any]:
        """Notifies DisasterBond contract about critical risk alerts."""
        try:
            return await self.client.notify_bond(
                lat=lat,
                lon=lon,
                risk_score_bps=risk_score_bps,
                assessment_id=assessment_id
            )
        except Exception as e:
            logger.error(f"Bond notification failed: {e}")
            return {"error": str(e)}


risk_anchor_service = RiskAnchorService()
