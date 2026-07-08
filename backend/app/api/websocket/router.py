from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from jose import jwt, JWTError
from app.core.config import settings
from app.api.websocket.manager import manager
from app.infrastructure.repositories.iam import SQLAlchemyUserRepository
from app.core.database import SessionLocal

router = APIRouter(prefix="/ws", tags=["WebSockets"])

async def get_user_from_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id:
            db = SessionLocal()
            try:
                return SQLAlchemyUserRepository(db).get_by_id(user_id)
            finally:
                db.close()
    except JWTError:
        return None
    return None

@router.websocket("/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    user = await get_user_from_token(token)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket, user.id)
    try:
        while True:
            await websocket.receive_text() # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket, user.id)
