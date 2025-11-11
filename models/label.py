from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from database import Base
from models.association_tables import cards_labels
class Label(Base):
    __tablename__ = "labels"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    color = Column(String, nullable=False)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False)
    board: Mapped["Board"] = relationship("Board", back_populates="labels")
    cards: Mapped[list["Card"]] = relationship(
        "Card",
        secondary=cards_labels,
        back_populates="labels"
    )