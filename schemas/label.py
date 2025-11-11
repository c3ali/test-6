from datetime import datetime
from pydantic import BaseModel
from schemas import BaseSchema
class LabelBase(BaseSchema):
    name: str
    color: str
    board_id: int | None = None
class LabelCreate(LabelBase):
    pass
class LabelUpdate(BaseSchema):
    name: str | None = None
    color: str | None = None
    board_id: int | None = None
class LabelResponse(LabelBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True