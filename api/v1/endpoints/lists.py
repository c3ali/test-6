from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import logging
from database import get_db
from models import List, Board, User
from schemas import ListSchema, ListCreate, ListUpdate, ListReorder
from services.board_service import BoardService
from auth.dependencies import get_current_user
from utils.exceptions import NotFoundException, ForbiddenException
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/lists", tags=["lists"])
@router.get("/board/{board_id}", response_model=list[ListSchema])
def get_lists_by_board(
    board_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    board_service = BoardService(db)
    if not board_service.user_has_access(board_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this board"
        )
    lists = db.query(List).filter(List.board_id == board_id).order_by(List.position).all()
    return lists
@router.get("/{list_id}", response_model=ListSchema)
def get_list(
    list_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    list_obj = db.query(List).filter(List.id == list_id).first()
    if not list_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found"
        )
    board_service = BoardService(db)
    if not board_service.user_has_access(list_obj.board_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this board"
        )
    return list_obj
@router.post("/", response_model=ListSchema, status_code=status.HTTP_201_CREATED)
def create_list(
    list_data: ListCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    board_service = BoardService(db)
    board = db.query(Board).filter(Board.id == list_data.board_id).first()
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    if not board_service.user_has_access(board.id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this board"
        )
    max_position = db.query(func.max(List.position)).filter(List.board_id == list_data.board_id).scalar()
    new_position = (max_position or 0) + 1
    new_list = List(
        title=list_data.title,
        board_id=list_data.board_id,
        position=new_position
    )
    try:
        db.add(new_list)
        db.commit()
        db.refresh(new_list)
        logger.info(f"List created: {new_list.id} by user {current_user.id}")
        return new_list
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create list"
        )
@router.put("/{list_id}", response_model=ListSchema)
def update_list(
    list_id: int,
    list_data: ListUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    list_obj = db.query(List).filter(List.id == list_id).with_for_update().first()
    if not list_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found"
        )
    board_service = BoardService(db)
    if not board_service.user_has_access(list_obj.board_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this board"
        )
    update_data = list_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(list_obj, field, value)
    try:
        db.commit()
        db.refresh(list_obj)
        logger.info(f"List updated: {list_id} by user {current_user.id}")
        return list_obj
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating list {list_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update list"
        )
@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_list(
    list_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    list_obj = db.query(List).filter(List.id == list_id).with_for_update().first()
    if not list_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found"
        )
    board_service = BoardService(db)
    if not board_service.user_has_access(list_obj.board_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this board"
        )
    try:
        board_id = list_obj.board_id
        deleted_position = list_obj.position
        db.delete(list_obj)
        db.query(List).filter(
            and_(
                List.board_id == board_id,
                List.position > deleted_position
            )
        ).update(
            {"position": List.position - 1},
            synchronize_session=False
        )
        db.commit()
        logger.info(f"List deleted: {list_id} by user {current_user.id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting list {list_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete list"
        )
@router.put("/{list_id}/reorder", response_model=ListSchema)
def reorder_list(
    list_id: int,
    reorder_data: ListReorder,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    list_obj = db.query(List).filter(List.id == list_id).with_for_update().first()
    if not list_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found"
        )
    board_service = BoardService(db)
    if not board_service.user_has_access(list_obj.board_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this board"
        )
    new_position = reorder_data.new_position
    list_count = db.query(func.count(List.id)).filter(List.board_id == list_obj.board_id).scalar()
    if new_position < 1 or new_position > list_count:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid position"
        )
    old_position = list_obj.position
    if old_position == new_position:
        return list_obj
    try:
        if new_position < old_position:
            db.query(List).filter(
                and_(
                    List.board_id == list_obj.board_id,
                    List.position >= new_position,
                    List.position < old_position
                )
            ).update(
                {"position": List.position + 1},
                synchronize_session=False
            )
        else:
            db.query(List).filter(
                and_(
                    List.board_id == list_obj.board_id,
                    List.position > old_position,
                    List.position <= new_position
                )
            ).update(
                {"position": List.position - 1},
                synchronize_session=False
            )
        list_obj.position = new_position
        db.commit()
        db.refresh(list_obj)
        logger.info(f"List reordered: {list_id} from {old_position} to {new_position} by user {current_user.id}")
        return list_obj
    except Exception as e:
        db.rollback()
        logger.error(f"Error reordering list {list_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reorder list"
        )