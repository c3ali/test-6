from datetime import datetime
from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from schemas.card import CardResponse
class ListBase(BaseModel):
    title: str
    board_id: int
    position: Optional[int] = None
class ListCreate(ListBase):
    pass
class ListUpdate(BaseModel):
    title: Optional[str] = None
    board_id: Optional[int] = None
    position: Optional[int] = None
class ListResponse(ListBase):
    id: int
    created_at: datetime
    updated_at: datetime
    cards: list["CardResponse"] = []
    model_config = ConfigDict(from_attributes=True)