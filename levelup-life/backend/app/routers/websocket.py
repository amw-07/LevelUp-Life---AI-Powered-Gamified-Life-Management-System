from fastapi import APIRouter, WebSocket, WebSocketDisconnect, WebSocketException, status
from app.utils.websocket_manager import ws_manager

router = APIRouter()


@router.websocket("/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, token: str | None = None):
    if token:
        try:
            from app.services.auth_service import decode_token
            payload = decode_token(token)
            if payload.get("type") != "access" or payload.get("sub") != user_id:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
        except Exception:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    await ws_manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(user_id)
