from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from schemas.user import UserResponse
class CommentBase(BaseModel):
    content: str
class CommentCreate(CommentBase):
    card_id: int
class CommentUpdate(BaseModel):
    content: Optional[str] = None
class CommentResponse(CommentBase):
    id: int
    card_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    user: UserResponse
    model_config = ConfigDict(from_attributes=True)