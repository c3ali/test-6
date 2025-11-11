from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from .user import UserResponse
from .comment import CommentResponse
from .label import LabelResponse
class CardBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
class CardCreate(CardBase):
    list_id: int
    position: Optional[int] = None
    assigned_user_id: Optional[int] = None
class CardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    list_id: Optional[int] = None
    position: Optional[int] = None
    assigned_user_id: Optional[int] = None
class CardResponse(CardBase):
    id: int
    list_id: int
    position: int
    assigned_user: Optional[UserResponse] = None
    comments: list[CommentResponse] = []
    labels: list[LabelResponse] = []
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)