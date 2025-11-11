from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from models import Card, CardHistory, Comment, Label, List, Board, User, BoardMember
from schemas import CardCreate, CardUpdate, CardMove
from services.notification_service import NotificationService
from repositories.board_repository import BoardRepository
from utils.exceptions import PermissionError, NotFoundError, ValidationError
class CardService:
    def __init__(self, db: Session, notification_service: NotificationService):
        self.db = db
        self.notification_service = notification_service
        self.board_repository = BoardRepository(db)
    def _check_board_permission(self, board_id: int, user_id: int, require_admin: bool = False) -> Board:
        board = self.db.query(Board).filter(Board.id == board_id).first()
        if not board:
            raise NotFoundError("Board not found")
        if not self.board_repository.has_permission(board_id, user_id, require_admin):
            raise PermissionError("Access denied to this board")
        return board
    def _get_card_with_permissions(self, card_id: int, user_id: int) -> Card:
        card = self.db.query(Card).options(
            joinedload(Card.list).joinedload(List.board),
            joinedload(Card.labels),
            joinedload(Card.assignees),
            joinedload(Card.comments)
        ).filter(Card.id == card_id).first()
        if not card:
            raise NotFoundError("Card not found")
        self._check_board_permission(card.list.board_id, user_id)
        return card
    def create_card(self, card_data: CardCreate, user_id: int) -> Card:
        board_list = self.db.query(List).filter(List.id == card_data.list_id).first()
        if not board_list:
            raise NotFoundError("List not found")
        self._check_board_permission(board_list.board_id, user_id)
        max_position = self.db.query(Card).filter(
            Card.list_id == card_data.list_id
        ).order_by(Card.position.desc()).first()
        position = (max_position.position + 1) if max_position else 0
        card = Card(
            title=card_data.title,
            description=card_data.description,
            list_id=card_data.list_id,
            position=position,
            due_date=card_data.due_date,
            created_by_id=user_id
        )
        self.db.add(card)
        self.db.commit()
        self.db.refresh(card)
        self.notification_service.create_card_notification(
            board_list.board_id,
            user_id,
            card.id,
            card.title
        )
        history_entry = CardHistory(
            card_id=card.id,
            user_id=user_id,
            action="created",
            details={"title": card.title, "list_id": card.list_id}
        )
        self.db.add(history_entry)
        self.db.commit()
        return card
    def get_card(self, card_id: int, user_id: int) -> Card:
        return self._get_card_with_permissions(card_id, user_id)
    def update_card(self, card_id: int, card_data: CardUpdate, user_id: int) -> Card:
        card = self._get_card_with_permissions(card_id, user_id)
        changes = {}
        for field, value in card_data.dict(exclude_unset=True).items():
            old_value = getattr(card, field)
            if old_value != value:
                changes[field] = {"old": old_value, "new": value}
                setattr(card, field, value)
        card.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(card)
        if changes:
            self.notification_service.update_card_notification(
                card.list.board_id,
                user_id,
                card.id,
                card.title,
                changes
            )
            history_entry = CardHistory(
                card_id=card.id,
                user_id=user_id,
                action="updated",
                details=changes
            )
            self.db.add(history_entry)
            self.db.commit()
        return card
    def delete_card(self, card_id: int, user_id: int) -> None:
        card = self._get_card_with_permissions(card_id, user_id)
        board_id = card.list.board_id
        card_title = card.title
        self.db.delete(card)
        self.db.commit()
        self.notification_service.delete_card_notification(
            board_id,
            user_id,
            card_title
        )
    def move_card(self, card_id: int, move_data: CardMove, user_id: int) -> Card:
        card = self._get_card_with_permissions(card_id, user_id)
        new_list = self.db.query(List).filter(List.id == move_data.new_list_id).first()
        if not new_list:
            raise NotFoundError("Target list not found")
        if card.list.board_id != new_list.board_id:
            self._check_board_permission(new_list.board_id, user_id)
        old_list_id = card.list_id
        old_position = card.position
        card.list_id = move_data.new_list_id
        card.position = move_data.new_position
        self._reorder_cards(old_list_id, exclude_card_id=card_id)
        self._reorder_cards(move_data.new_list_id, exclude_card_id=card_id)
        card.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(card)
        self.notification_service.move_card_notification(
            card.list.board_id,
            user_id,
            card.id,
            card.title,
            old_list_id,
            move_data.new_list_id
        )
        history_entry = CardHistory(
            card_id=card.id,
            user_id=user_id,
            action="moved",
            details={
                "old_list_id": old_list_id,
                "new_list_id": move_data.new_list_id,
                "old_position": old_position,
                "new_position": move_data.new_position
            }
        )
        self.db.add(history_entry)
        self.db.commit()
        return card
    def _reorder_cards(self, list_id: int, exclude_card_id: Optional[int] = None) -> None:
        cards = self.db.query(Card).filter(
            Card.list_id == list_id
        ).order_by(Card.position).all()
        for index, card in enumerate(cards):
            if card.id != exclude_card_id:
                card.position = index
        self.db.commit()
    def add_comment(self, card_id: int, content: str, user_id: int) -> Comment:
        card = self._get_card_with_permissions(card_id, user_id)
        comment = Comment(
            content=content,
            card_id=card_id,
            user_id=user_id
        )
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        self.notification_service.comment_notification(
            card.list.board_id,
            user_id,
            card_id,
            card.title,
            comment.content
        )
        return comment
    def add_label_to_card(self, card_id: int, label_id: int, user_id: int) -> Card:
        card = self._get_card_with_permissions(card_id, user_id)
        label = self.db.query(Label).filter(Label.id == label_id).first()
        if not label:
            raise NotFoundError("Label not found")
        if label.board_id != card.list.board_id:
            raise ValidationError("Label does not belong to this board")
        if label not in card.labels:
            card.labels.append(label)
            card.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(card)
            history_entry = CardHistory(
                card_id=card.id,
                user_id=user_id,
                action="label_added",
                details={"label_id": label_id, "label_name": label.name, "label_color": label.color}
            )
            self.db.add(history_entry)
            self.db.commit()
        return card
    def remove_label_from_card(self, card_id: int, label_id: int, user_id: int) -> Card:
        card = self._get_card_with_permissions(card_id, user_id)
        label = self.db.query(Label).filter(Label.id == label_id).first()
        if not label:
            raise NotFoundError("Label not found")
        if label in card.labels:
            card.labels.remove(label)
            card.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(card)
            history_entry = CardHistory(
                card_id=card.id,
                user_id=user_id,
                action="label_removed",
                details={"label_id": label_id, "label_name": label.name}
            )
            self.db.add(history_entry)
            self.db.commit()
        return card
    def assign_user_to_card(self, card_id: int, assignee_id: int, user_id: int) -> Card:
        card = self._get_card_with_permissions(card_id, user_id)
        assignee = self.db.query(User).filter(User.id == assignee_id).first()
        if not assignee:
            raise NotFoundError("User not found")
        board_member = self.db.query(BoardMember).filter(
            and_(
                BoardMember.board_id == card.list.board_id,
                BoardMember.user_id == assignee_id
            )
        ).first()
        if not board_member:
            raise ValidationError("User is not a member of this board")
        if assignee not in card.assignees:
            card.assignees.append(assignee)
            card.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(card)
            self.notification_service.assignment_notification(
                card.list.board_id,
                user_id,
                assignee_id,
                card.id,
                card.title
            )
            history_entry = CardHistory(
                card_id=card.id,
                user_id=user_id,
                action="user_assigned",
                details={"assignee_id": assignee_id, "assignee_email": assignee.email}
            )
            self.db.add(history_entry)
            self.db.commit()
        return card
    def remove_user_from_card(self, card_id: int, assignee_id: int, user_id: int) -> Card:
        card = self._get_card_with_permissions(card_id, user_id)
        assignee = self.db.query(User).filter(User.id == assignee_id).first()
        if not assignee:
            raise NotFoundError("User not found")
        if assignee in card.assignees:
            card.assignees.remove(assignee)
            card.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(card)
            history_entry = CardHistory(
                card_id=card.id,
                user_id=user_id,
                action="user_unassigned",
                details={"assignee_id": assignee_id, "assignee_email": assignee.email}
            )
            self.db.add(history_entry)
            self.db.commit()
        return card
    def get_card_history(self, card_id: int, user_id: int) -> list[CardHistory]:
        card = self._get_card_with_permissions(card_id, user_id)
        history = self.db.query(CardHistory).filter(
            CardHistory.card_id == card_id
        ).order_by(CardHistory.timestamp.desc()).all()
        return history