from sqlalchemy import ForeignKey, func, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from database import Base
from models.association_tables import cards_labels
class Card(Base):
    __tablename__ = "cards"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    position: Mapped[int] = mapped_column(nullable=False)
    list_id: Mapped[int] = mapped_column(ForeignKey("lists.id"))
    assigned_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    list: Mapped["List"] = relationship(back_populates="cards")
    assigned_user: Mapped["User | None"] = relationship(back_populates="assigned_cards")
    comments: Mapped[list["Comment"]] = relationship(back_populates="card", cascade="all, delete-orphan")
    labels: Mapped[list["Label"]] = relationship(secondary=cards_labels, back_populates="cards")
    __table_args__ = (
        Index("idx_cards_list_id", "list_id"),
        Index("idx_cards_assigned_user_id", "assigned_user_id"),
        Index("idx_cards_due_date", "due_date"),
    )