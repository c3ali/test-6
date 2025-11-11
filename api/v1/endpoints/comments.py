from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from auth.dependencies import get_current_user
from models import User, Comment, Card
from schemas import CommentCreate, CommentUpdate, CommentResponse
from services.card_service import CardService
from utils.exceptions import NotFoundException, ForbiddenException
router = APIRouter()
@router.get("/cards/{card_id}/comments", response_model=list[CommentResponse])
def get_comments_by_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    card_service = CardService(db)
    try:
        card = card_service.get_card(card_id)
        board = card.list.board
        if current_user not in board.members and board.owner_id != current_user.id:
            raise ForbiddenException("You don't have access to this board")
    except NotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    comments = db.query(Comment).filter(Comment.card_id == card_id).order_by(Comment.created_at.desc()).all()
    return comments
@router.post("/cards/{card_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    card_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    card_service = CardService(db)
    try:
        card = card_service.get_card(card_id)
        board = card.list.board
        if current_user not in board.members and board.owner_id != current_user.id:
            raise ForbiddenException("You don't have access to this board")
    except NotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    new_comment = Comment(
        content=comment_data.content,
        card_id=card_id,
        author_id=current_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment
@router.put("/comments/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own comments")
    comment.content = comment_data.content
    comment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(comment)
    return comment
@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    board = comment.card.list.board
    if comment.author_id != current_user.id and board.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to delete this comment")
    db.delete(comment)
    db.commit()
    return None