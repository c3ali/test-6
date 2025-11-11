from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException
from sqlalchemy.orm import Session
import json
from jose import JWTError
from auth.jwt_handler import verify_token
from database import get_db
from models import User
from services.board_service import BoardService
router = APIRouter()
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}
    async def connect(self, board_id: int, websocket: WebSocket):
        await websocket.accept()
        if board_id not in self.active_connections:
            self.active_connections[board_id] = []
        self.active_connections[board_id].append(websocket)
    def disconnect(self, board_id: int, websocket: WebSocket):
        if board_id in self.active_connections:
            self.active_connections[board_id].remove(websocket)
            if not self.active_connections[board_id]:
                del self.active_connections[board_id]
manager = ConnectionManager()
@router.websocket("/ws/boards/{board_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    board_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=1008, reason="Invalid token")
            return
    except JWTError:
        await websocket.close(code=1008, reason="Invalid token")
        return
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        await websocket.close(code=1008, reason="User not found")
        return
    board_service = BoardService(db)
    try:
        board = await board_service.get_board(board_id)
        if not board or not any(member.user_id == user.id for member in board.members):
            await websocket.close(code=1008, reason="Access denied")
            return
    except Exception:
        await websocket.close(code=1011, reason="Internal error")
        return
    await manager.connect(board_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(board_id, websocket)