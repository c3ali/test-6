from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from schemas.user import UserResponse
    from schemas.list import ListResponse
class BoardBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_public: bool = False
class BoardCreate(BoardBase):
    pass
class BoardUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_public: Optional[bool] = None
class BoardResponse(BoardBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    members: list["UserResponse"] = Field(default_factory=list)
    lists: list["ListResponse"] = Field(default_factory=list)
    model_config = {"from_attributes": True}