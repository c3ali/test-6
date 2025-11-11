import logging
import json
from datetime import datetime
from typing import Any
from redis.asyncio import Redis
from models import User, Board, Card, Comment, Label
from schemas import WebSocketMessage, NotificationType, NotificationData
from config import settings
logger = logging.getLogger(__name__)
class NotificationService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    def _create_notification(
        self,
        notification_type: NotificationType,
        title: str,
        message: str,
        resource_id: int,
        resource_type: str,
        user_id: int,
        board_id: int,
        additional_data: dict[str, Any] | None = None
    ) -> NotificationData:
        return NotificationData(
            type=notification_type,
            title=title,
            message=message,
            resource_id=resource_id,
            resource_type=resource_type,
            user_id=user_id,
            board_id=board_id,
            additional_data=additional_data or {},
            timestamp=datetime.utcnow()
        )
    async def _publish(self, board_id: int, notification: NotificationData):
        channel = f"board:{board_id}:notifications"
        message = WebSocketMessage(type="notification", data=notification.dict())
        await self.redis.publish(channel, message.json())
    async def notify_card_created(self, card: Card, creator: User):
        notification = self._create_notification(
            NotificationType.CARD_CREATED,
            f"Nouvelle carte : {card.title}",
            f"{creator.username} a créé une carte dans {card.list.title}",
            card.id,
            "card",
            creator.id,
            card.list.board_id,
            {"list_id": card.list_id, "card_title": card.title}
        )
        await self._publish(card.list.board_id, notification)
    async def notify_card_updated(self, card: Card, updater: User, changes: dict[str, Any]):
        notification = self._create_notification(
            NotificationType.CARD_UPDATED,
            f"Carte modifiée : {card.title}",
            f"{updater.username} a mis à jour la carte",
            card.id,
            "card",
            updater.id,
            card.list.board_id,
            {"changes": changes, "card_title": card.title}
        )
        await self._publish(card.list.board_id, notification)
    async def notify_card_moved(self, card: Card, old_list_title: str, new_list_title: str, mover: User):
        notification = self._create_notification(
            NotificationType.CARD_MOVED,
            f"Carte déplacée : {card.title}",
            f"{mover.username} a déplacé la carte de '{old_list_title}' à '{new_list_title}'",
            card.id,
            "card",
            mover.id,
            card.list.board_id,
            {
                "card_title": card.title,
                "old_list_title": old_list_title,
                "new_list_title": new_list_title
            }
        )
        await self._publish(card.list.board_id, notification)
    async def notify_comment_added(self, comment: Comment, card: Card, commenter: User):
        notification = self._create_notification(
            NotificationType.COMMENT_ADDED,
            f"Nouveau commentaire sur : {card.title}",
            f"{commenter.username} : {comment.content[:100]}...",
            comment.id,
            "comment",
            commenter.id,
            card.list.board_id,
            {
                "card_id": card.id,
                "card_title": card.title,
                "comment_preview": comment.content[:100]
            }
        )
        await self._publish(card.list.board_id, notification)
    async def notify_label_added(self, card: Card, label: Label, user: User):
        notification = self._create_notification(
            NotificationType.LABEL_ADDED,
            f"Label ajouté à : {card.title}",
            f"{user.username} a ajouté le label '{label.name}'",
            label.id,
            "label",
            user.id,
            card.list.board_id,
            {
                "card_id": card.id,
                "card_title": card.title,
                "label_name": label.name,
                "label_color": label.color
            }
        )
        await self._publish(card.list.board_id, notification)
    async def notify_member_added_to_board(self, board: Board, new_member: User, added_by: User):
        notification = self._create_notification(
            NotificationType.MEMBER_ADDED,
            f"Nouveau membre dans {board.title}",
            f"{added_by.username} a ajouté {new_member.username} au board",
            board.id,
            "board",
            added_by.id,
            board.id,
            {
                "new_member_id": new_member.id,
                "new_member_username": new_member.username
            }
        )
        await self._publish(board.id, notification)
    async def notify_board_updated(self, board: Board, updater: User, changes: dict[str, Any]):
        notification = self._create_notification(
            NotificationType.BOARD_UPDATED,
            f"Board modifié : {board.title}",
            f"{updater.username} a mis à jour le board",
            board.id,
            "board",
            updater.id,
            board.id,
            {"changes": changes}
        )
        await self._publish(board.id, notification)