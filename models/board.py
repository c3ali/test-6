from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from models.user import User
from models.list import List
from models.association_tables import board_members
class Board(Base):
    __tablename__ = "boards"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    owner: Mapped[User] = relationship("User", back_populates="owned_boards")
    lists: Mapped[list["List"]] = relationship("List", back_populates="board", cascade="all, delete-orphan")
    members: Mapped[list[User]] = relationship("User", secondary=board_members, back_populates="member_boards")