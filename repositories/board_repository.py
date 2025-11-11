from typing import Optional, List
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import select
from models import Board, User, List, Card, Label
from schemas import BoardCreate, BoardUpdate
from repositories.base import BaseRepository
class BoardRepository(BaseRepository[Board, BoardCreate, BoardUpdate]):
    def __init__(self, db: Session):
        super().__init__(db, Board)
    def get_with_relations(self, board_id: int) -> Optional[Board]:
        query = select(Board).where(Board.id == board_id).options(
            joinedload(Board.owner),
            joinedload(Board.members),
            selectinload(Board.lists).selectinload(List.cards).selectinload(Card.labels),
            selectinload(Board.lists).selectinload(List.cards).selectinload(Card.assignees),
            selectinload(Board.labels)
        )
        result = self.db.execute(query)
        return result.scalar_one_or_none()
    def get_by_owner(self, owner_id: int) -> List[Board]:
        query = select(Board).where(Board.owner_id == owner_id).options(
            joinedload(Board.owner),
            joinedload(Board.members),
            selectinload(Board.lists),
            selectinload(Board.labels)
        ).order_by(Board.created_at.desc())
        result = self.db.execute(query)
        return result.scalars().all()
    def get_by_member(self, user_id: int) -> List[Board]:
        query = select(Board).join(Board.members).where(User.id == user_id).options(
            joinedload(Board.owner),
            joinedload(Board.members),
            selectinload(Board.lists),
            selectinload(Board.labels)
        ).order_by(Board.created_at.desc())
        result = self.db.execute(query)
        return result.scalars().all()
    def create_with_owner(self, board_data: BoardCreate, owner_id: int) -> Board:
        db_board = Board(**board_data.model_dump(exclude_unset=True), owner_id=owner_id)
        self.db.add(db_board)
        self.db.flush()
        self.db.refresh(db_board)
        return db_board
    def add_member(self, board_id: int, user_id: int) -> bool:
        board = self.get(board_id)
        if not board:
            return False
        user = self.db.get(User, user_id)
        if not user:
            return False
        if user not in board.members:
            board.members.append(user)
            self.db.flush()
        return True
    def remove_member(self, board_id: int, user_id: int) -> bool:
        board = self.get(board_id)
        if not board:
            return False
        user = self.db.get(User, user_id)
        if not user:
            return False
        if user in board.members:
            board.members.remove(user)
            self.db.flush()
            return True
        return False
    def get_board_summary(self, board_id: int) -> Optional[dict]:
        board = self.get_with_relations(board_id)
        if not board:
            return None
        total_lists = len(board.lists)
        total_cards = sum(len(lst.cards) for lst in board.lists)
        return {
            "board": board,
            "stats": {
                "total_lists": total_lists,
                "total_cards": total_cards,
                "total_members": len(board.members),
                "total_labels": len(board.labels)
            }
        }