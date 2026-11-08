"""
CrowdWisdom AI Studio — WebSocket Manager
Manages real-time connections for agent status, job progress, and notifications.
"""
import json
import logging
from typing import Dict, List, Optional, Any
from fastapi import WebSocket
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        # client_id → list of active WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Campaign-level subscribers
        self.campaign_subscribers: Dict[str, List[str]] = {}  # campaign_id → [client_ids]

    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        try:
            from starlette.websockets import WebSocketState
            if websocket.client_state == WebSocketState.CONNECTING:
                await websocket.accept()
        except Exception:
            pass
        if client_id not in self.active_connections:
            self.active_connections[client_id] = []
        self.active_connections[client_id].append(websocket)
        logger.info(f"WebSocket connected: {client_id}")

    def disconnect(self, websocket: WebSocket, client_id: str) -> None:
        if client_id in self.active_connections:
            try:
                self.active_connections[client_id].remove(websocket)
                if not self.active_connections[client_id]:
                    del self.active_connections[client_id]
            except ValueError:
                pass
        logger.info(f"WebSocket disconnected: {client_id}")

    async def send_to_client(self, client_id: str, message: dict) -> None:
        if client_id in self.active_connections:
            dead = []
            for ws in self.active_connections[client_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                self.disconnect(ws, client_id)

    async def broadcast_to_all(self, message: dict) -> None:
        for client_id in list(self.active_connections.keys()):
            await self.send_to_client(client_id, message)

    async def broadcast_campaign_event(
        self, campaign_id: str, event_type: str, data: Any
    ) -> None:
        """Broadcast an event to all clients subscribed to a campaign."""
        message = {
            "type": event_type,
            "campaign_id": campaign_id,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }
        # Broadcast to all connected clients (frontend filters by campaign_id)
        await self.broadcast_to_all(message)

    async def send_job_progress(
        self,
        job_id: str,
        job_type: str,
        campaign_id: str,
        status: str,
        progress_percent: int,
        current_stage: Optional[str] = None,
        data: Optional[dict] = None,
    ) -> None:
        """Send job progress update to all connected clients."""
        message = {
            "type": "job_progress",
            "job_id": job_id,
            "job_type": job_type,
            "campaign_id": campaign_id,
            "status": status,
            "progress_percent": progress_percent,
            "current_stage": current_stage,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.broadcast_to_all(message)

    async def send_agent_status(
        self,
        agent_type: str,
        campaign_id: str,
        status: str,
        task: Optional[str] = None,
        execution_id: Optional[str] = None,
    ) -> None:
        """Broadcast agent status change."""
        message = {
            "type": "agent_status",
            "agent_type": agent_type,
            "campaign_id": campaign_id,
            "status": status,
            "current_task": task,
            "execution_id": execution_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.broadcast_to_all(message)

    async def send_notification(
        self, title: str, message_text: str, category: str, action_url: Optional[str] = None
    ) -> None:
        """Broadcast a user notification."""
        message = {
            "type": "notification",
            "title": title,
            "message": message_text,
            "category": category,
            "action_url": action_url,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.broadcast_to_all(message)


# Global singleton
ws_manager = ConnectionManager()

