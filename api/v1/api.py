from fastapi import APIRouter
from api.v1.endpoints import auth, users, boards, lists, cards, comments, labels, websocket
api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(boards.router, prefix="/boards", tags=["boards"])
api_router.include_router(lists.router, prefix="/lists", tags=["lists"])
api_router.include_router(cards.router, prefix="/cards", tags=["cards"])
api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
api_router.include_router(labels.router, prefix="/labels", tags=["labels"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])