"""
CrowdWisdom AI Studio — WebSocket API Route
Real-time updates for agent status, job progress, and notifications.
"""
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from services.websocket_manager import ws_manager
from services.auth_service import decode_access_token

logger = logging.getLogger(__name__)
router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, token: str = Query(None)):
    """
    WebSocket endpoint for real-time updates.
    Clients connect with their client_id (usually user_id or session_id).
    Optional token param for authentication.
    """
    # Accept first, then reject with WS close code (not HTTP 403) so browser
    # can read the close code and stop reconnecting on token expiry.
    await websocket.accept()

    if token:
        payload = decode_access_token(token)
        if not payload:
            await websocket.close(code=4001, reason="Invalid or expired authentication token.")
            return

    await ws_manager.connect(websocket, client_id)
    logger.info(f"WebSocket client connected: {client_id}")

    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "client_id": client_id,
            "message": "Connected to CrowdWisdom AI Studio real-time channel.",
        })

        # Keep connection alive and listen for client messages
        while True:
            try:
                data = await websocket.receive_json()
                # Handle client-to-server messages (e.g., subscribe to campaign)
                msg_type = data.get("type")
                if msg_type == "ping":
                    await websocket.send_json({"type": "pong"})
                elif msg_type == "subscribe":
                    # Client subscribing to campaign events
                    campaign_id = data.get("campaign_id")
                    if campaign_id:
                        await websocket.send_json({
                            "type": "subscribed",
                            "campaign_id": campaign_id,
                        })
            except Exception:
                break

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, client_id)
        logger.info(f"WebSocket client disconnected: {client_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        ws_manager.disconnect(websocket, client_id)

