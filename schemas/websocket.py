from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field
class WebSocketAction(str, Enum):
    CARD_MOVE = "card_move"
    COMMENT_ADD = "comment_add"
    CARD_CREATE = "card_create"
    CARD_UPDATE = "card_update"
    CARD_DELETE = "card_delete"
    LIST_CREATE = "list_create"
    LIST_UPDATE = "list_update"
    LIST_DELETE = "list_delete"
    BOARD_UPDATE = "board_update"
    BOARD_DELETE = "board_delete"
    LABEL_ADD = "label_add"
    LABEL_REMOVE = "label_remove"
    MEMBER_ADD = "member_add"
    MEMBER_REMOVE = "member_remove"
class WebSocketMessage(BaseModel):
    action: WebSocketAction
    data: dict[str, Any]
    user_id: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    board_id: Optional[int] = None
class CardMoveData(BaseModel):
    card_id: int
    from_list_id: int
    to_list_id: int
    new_position: int
    old_position: Optional[int] = None
class CommentAddData(BaseModel):
    card_id: int
    content: str
    parent_comment_id: Optional[int] = None
class CardCreateData(BaseModel):
    list_id: int
    title: str
    description: Optional[str] = None
    position: Optional[int] = None
class CardUpdateData(BaseModel):
    card_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    position: Optional[int] = None
    list_id: Optional[int] = None
class CardDeleteData(BaseModel):
    card_id: int
    list_id: int
class ListCreateData(BaseModel):
    board_id: int
    title: str
    position: Optional[int] = None
class ListUpdateData(BaseModel):
    list_id: int
    title: Optional[str] = None
    position: Optional[int] = None
class ListDeleteData(BaseModel):
    list_id: int
class BoardUpdateData(BaseModel):
    board_id: int
    name: Optional[str] = None
    description: Optional[str] = None
    is_archived: Optional[bool] = None
class BoardDeleteData(BaseModel):
    board_id: int
class LabelAddData(BaseModel):
    card_id: int
    label_id: int
class LabelRemoveData(BaseModel):
    card_id: int
    label_id: int
class MemberAddData(BaseModel):
    board_id: int
    user_id: int
    role: str
class MemberRemoveData(BaseModel):
    board_id: int
    user_id: int
class CardMoveMessage(WebSocketMessage):
    action: WebSocketAction = WebSocketAction.CARD_MOVE
    data: CardMoveData
class CommentAddMessage(WebSocketMessage):
    action: WebSocketAction = WebSocketAction.COMMENT_ADD
    data: CommentAddData
class CardCreateMessage(WebSocketMessage):
    action: WebSocketAction = WebSocketAction.CARD_CREATE
    data: CardCreateData
class CardUpdateMessage(WebSocketMessage):
    action: WebSocketAction = WebSocketAction.CARD_UPDATE
    data: CardUpdateData
class CardDeleteMessage(WebSocketMessage):
    action: WebSocketAction = WebSocketAction.CARD_DELETE
    data: CardDeleteData
class ListCreateMessage(WebSocketMessage):
    action: WebSocketAction = WebSocketAction.LIST_CREATE
    data: ListCreateData
class ListUpdateMessage(WebSocketMessage):
    action: WebSocketAction = WebSocketAction.LIST_UPDATE
    data: ListUpdateData
class ListDeleteMessage(WebSocketMessage):
    action: WebSocketAction = WebSocketAction.LIST_DELETE
    data: ListDeleteData
class BoardUpdateMessage(WebSocketMessage):
    action: WebSocketAction = WebSocketAction.BOARD_UPDATE
    data: BoardUpdateData
class BoardDeleteMessage(WebSocketMessage):
    action: WebSocketAction = WebSocketAction.BOARD_DELETE
    data: BoardDeleteData
class LabelAddMessage(WebSocketMessage):
    action: WebSocketAction = WebSocketAction.LABEL_ADD
    data: LabelAddData
class LabelRemoveMessage(WebSocketMessage):
    action: WebSocketAction = WebSocketAction.LABEL_REMOVE
    data: LabelRemoveData
class MemberAddMessage(WebSocketMessage):
    action: WebSocketAction = WebSocketAction.MEMBER_ADD
    data: MemberAddData
class MemberRemoveMessage(WebSocketMessage):
    action: WebSocketAction = WebSocketAction.MEMBER_REMOVE
    data: MemberRemoveData