from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func
from database import Base
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    avatar_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    boards: Mapped[list["Board"]] = relationship("Board", back_populates="owner", cascade="all, delete-orphan")
    cards: Mapped[list["Card"]] = relationship("Card", back_populates="user", cascade="all, delete-orphan")