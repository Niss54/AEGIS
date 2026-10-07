"""
WebSocket Connection Manager for AEGIS-CLIMATE
Handles real-time streaming of multi-agent execution steps, thought traces, and event broadcasts.
"""
import json
import logging
from typing import List, Dict, Any
from fastapi import WebSocket

logger = logging.getLogger("aegis.websocket")


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Active connections: {len(self.active_connections)}")
        # Send welcome handshake safely
        try:
            await websocket.send_text(json.dumps({
                "type": "HANDSHAKE",
                "message": "Connected to AEGIS-CLIMATE Real-Time Multi-Agent Stream",
                "active_clients": len(self.active_connections)
            }))
        except Exception as e:
            logger.debug(f"Handshake send skipped: {e}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Remaining: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast JSON message to all connected clients."""
        if not self.active_connections:
            return
        
        payload = json.dumps(message)
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(payload)
            except Exception as e:
                logger.warning(f"Error broadcasting to client: {e}")
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(dead)

    async def broadcast_step(self, agent_id: str, step_name: str, action_type: str, content: str):
        """Broadcast single agent thought / tool call step for live visualization."""
        await self.broadcast({
            "type": "AGENT_STEP",
            "agent_id": agent_id,
            "step_name": step_name,
            "action_type": action_type,
            "content": content
        })


manager = ConnectionManager()
