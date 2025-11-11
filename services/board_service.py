from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timedelta
from models import Board, BoardMember, User, BoardInvitation, BoardActivity
from schemas import BoardCreate, BoardUpdate, BoardMemberResponse, InvitationCreate, InvitationResponse
from repositories.board_repository import BoardRepository
from repositories.user_repository import UserRepository
from services.notification_service import NotificationService
from utils.exceptions import NotFoundException, PermissionException
class BoardService:
    @staticmethod
    def _check_permission(
        db: Session, 
        board_id: int, 
        user: User, 
        required_roles: list[str],
        allow_public: bool = False
    ) -> Board:
        board = BoardRepository.get_board(db, board_id)
        if not board:
            raise NotFoundException(f"Board avec l'id {board_id} non trouvé")
        if allow_public and board.is_public:
            return board
        member = BoardRepository.get_member(db, board_id, user.id)
        if not member:
            raise PermissionException("Vous n'avez pas accès à ce board")
        if member.role not in required_roles:
            raise PermissionException(f"Rôle '{member.role}' insuffisant. Requis: {required_roles}")
        return board
    @staticmethod
    def get_board(db: Session, board_id: int, user: User) -> Board:
        return BoardService._check_permission(
            db, board_id, user, 
            required_roles=["viewer", "member", "admin"],
            allow_public=True
        )
    @staticmethod
    def get_user_boards(
        db: Session, 
        user: User, 
        skip: int = 0, 
        limit: int = 100,
        include_public: bool = True
    ) -> list[Board]:
        return BoardRepository.get_boards_by_user(
            db, user.id, skip=skip, limit=limit, include_public=include_public
        )
    @staticmethod
    def create_board(db: Session, board_data: BoardCreate, owner: User) -> Board:
        board = BoardRepository.create_board(db, board_data, owner.id)
        BoardRepository.add_member(db, board.id, owner.id, "admin")
        BoardService._log_activity(db, board.id, owner.id, "board_created", {"board_name": board.name})
        return board
    @staticmethod
    def update_board(
        db: Session, 
        board_id: int, 
        board_data: BoardUpdate, 
        user: User
    ) -> Board:
        BoardService._check_permission(db, board_id, user, required_roles=["admin"])
        updated_board = BoardRepository.update_board(db, board_id, board_data)
        BoardService._log_activity(
            db, board_id, user.id, "board_updated", 
            {"updated_fields": board_data.model_dump(exclude_unset=True)}
        )
        return updated_board
    @staticmethod
    def delete_board(db: Session, board_id: int, user: User) -> None:
        board = BoardService._check_permission(db, board_id, user, required_roles=["admin"])
        if board.owner_id != user.id:
            raise PermissionException("Seul le propriétaire peut supprimer le board")
        BoardService._log_activity(db, board_id, user.id, "board_deleted", {"board_name": board.name})
        BoardRepository.delete_board(db, board_id)
    @staticmethod
    def add_member(
        db: Session, 
        board_id: int, 
        invitation_data: InvitationCreate, 
        current_user: User
    ) -> InvitationResponse:
        BoardService._check_permission(db, board_id, current_user, required_roles=["admin"])
        invited_user = UserRepository.get_by_email(db, invitation_data.email)
        if invited_user:
            existing_member = BoardRepository.get_member(db, board_id, invited_user.id)
            if existing_member:
                raise PermissionException("Cet utilisateur est déjà membre du board")
        invitation = BoardInvitation(
            board_id=board_id,
            email=invitation_data.email,
            role=invitation_data.role,
            token=str(uuid.uuid4()),
            invited_by=current_user.id,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.add(invitation)
        db.commit()
        db.refresh(invitation)
        NotificationService.send_board_invitation(
            invitation_data.email, 
            current_user.username, 
            board_id,
            invitation.token
        )
        BoardService._log_activity(
            db, board_id, current_user.id, "member_invited", 
            {"invited_email": invitation_data.email, "role": invitation_data.role}
        )
        return invitation
    @staticmethod
    def remove_member(db: Session, board_id: int, user_id: int, current_user: User) -> None:
        board = BoardService._check_permission(db, board_id, current_user, required_roles=["admin"])
        if current_user.id == user_id:
            admin_count = BoardRepository.get_admin_count(db, board_id)
            if admin_count <= 1:
                raise PermissionException("Impossible de se supprimer : vous êtes le seul administrateur")
        if board.owner_id == user_id:
            raise PermissionException("Impossible de supprimer le propriétaire du board")
        member = BoardRepository.get_member(db, board_id, user_id)
        if not member:
            raise NotFoundException("Membre non trouvé")
        BoardRepository.remove_member(db, board_id, user_id)
        BoardService._log_activity(
            db, board_id, current_user.id, "member_removed", 
            {"removed_user_id": user_id}
        )
    @staticmethod
    def update_member_role(
        db: Session, 
        board_id: int, 
        user_id: int, 
        new_role: str, 
        current_user: User
    ) -> BoardMember:
        board = BoardService._check_permission(db, board_id, current_user, required_roles=["admin"])
        if board.owner_id == user_id:
            raise PermissionException("Impossible de modifier le rôle du propriétaire")
        member = BoardRepository.get_member(db, board_id, user_id)
        if not member:
            raise NotFoundException("Membre non trouvé")
        updated_member = BoardRepository.update_member_role(db, board_id, user_id, new_role)
        BoardService._log_activity(
            db, board_id, current_user.id, "member_role_updated", 
            {"user_id": user_id, "new_role": new_role}
        )
        return updated_member
    @staticmethod
    def accept_invitation(db: Session, token: str, user: User) -> Board:
        invitation = BoardRepository.get_invitation_by_token(db, token)
        if not invitation:
            raise NotFoundException("Invitation invalide")
        if invitation.email != user.email:
            raise PermissionException("Cette invitation n'est pas destinée à cette adresse email")
        if invitation.expires_at < datetime.utcnow():
            raise PermissionException("Invitation expirée")
        if invitation.used or invitation.declined:
            raise PermissionException("Invitation déjà utilisée ou déclinée")
        existing_member = BoardRepository.get_member(db, invitation.board_id, user.id)
        if existing_member:
            raise PermissionException("Vous êtes déjà membre de ce board")
        board_id = invitation.board_id
        BoardRepository.add_member(db, board_id, user.id, invitation.role)
        invitation.used = True
        invitation.used_at = datetime.utcnow()
        db.commit()
        BoardService._log_activity(
            db, board_id, user.id, "invitation_accepted", 
            {"role": invitation.role}
        )
        return BoardRepository.get_board(db, board_id)
    @staticmethod
    def decline_invitation(db: Session, token: str, user: User) -> None:
        invitation = BoardRepository.get_invitation_by_token(db, token)
        if not invitation:
            raise NotFoundException("Invitation invalide")
        if invitation.email != user.email:
            raise PermissionException("Cette invitation n'est pas destinée à cette adresse email")
        invitation.declined = True
        invitation.declined_at = datetime.utcnow()
        db.commit()
        BoardService._log_activity(
            db, invitation.board_id, user.id, "invitation_declined", 
            {}
        )
    @staticmethod
    def get_board_members(db: Session, board_id: int, user: User) -> list[BoardMemberResponse]:
        BoardService._check_permission(
            db, board_id, user, 
            required_roles=["viewer", "member", "admin"],
            allow_public=True
        )
        return BoardRepository.get_members_with_details(db, board_id)
    @staticmethod
    def _log_activity(
        db: Session, 
        board_id: int, 
        user_id: int, 
        action: str, 
        details: dict
    ) -> None:
        activity = BoardActivity(
            board_id=board_id,
            user_id=user_id,
            action=action,
            details=details,
            timestamp=datetime.utcnow()
        )
        db.add(activity)
        db.commit()