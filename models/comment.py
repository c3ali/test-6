from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, relationship
from datetime import datetime
from database import Base
class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    content: Mapped[str] = Column(Text, nullable=False)
    card_id: Mapped[int] = Column(Integer, ForeignKey("cards.id"), nullable=False)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    user: Mapped["User"] = relationship("User")