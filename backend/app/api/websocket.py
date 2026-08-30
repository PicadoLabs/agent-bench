import asyncio
from typing import Dict, List, Any
from fastapi import WebSocket


class WebSocketConnectionManager:
    """Manages WebSocket subscriptions for real-time live run telemetry streaming."""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, run_id: str, websocket: WebSocket):
        await websocket.accept()
        if run_id not in self.active_connections:
            self.active_connections[run_id] = []
        self.active_connections[run_id].append(websocket)

    def disconnect(self, run_id: str, websocket: WebSocket):
        if run_id in self.active_connections:
            if websocket in self.active_connections[run_id]:
                self.active_connections[run_id].remove(websocket)
            if not self.active_connections[run_id]:
                del self.active_connections[run_id]

    async def broadcast_event(self, run_id: str, message: Dict[str, Any]):
        if run_id in self.active_connections:
            dead_sockets = []
            for ws in self.active_connections[run_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead_sockets.append(ws)
            for ws in dead_sockets:
                self.disconnect(run_id, ws)


ws_manager = WebSocketConnectionManager()
