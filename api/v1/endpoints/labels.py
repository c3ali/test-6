from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Any
from models import Label, Board, Card, User, card_labels_association
from schemas import LabelCreate, LabelUpdate, LabelResponse
from auth.dependencies import get_current_active_user
from database import get_db
router = APIRouter()
def _check_board_access(board_id: int, user: User, db: Session) -> Board:
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    if board.owner_id != user.id and user not in board.members:
        raise HTTPException(status_code=403, detail="Not authorized to access this board")
    return board
def _get_label_with_access(label_id: int, user: User, db: Session) -> Label:
    label = db.query(Label).filter(Label.id == label_id).first()
    if not label:
        raise HTTPException(status_code=404, detail="Label not found")
    _check_board_access(label.board_id, user, db)
    return label
def _get_card_with_access(card_id: int, user: User, db: Session) -> Card:
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    _check_board_access(card.list.board_id, user, db)
    return card
@router.post("/", response_model=LabelResponse, status_code=status.HTTP_201_CREATED)
def create_label(
    label_data: LabelCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    _check_board_access(label_data.board_id, current_user, db)
    db_label = Label(
        name=label_data.name,
        color=label_data.color,
        board_id=label_data.board_id
    )
    db.add(db_label)
    db.commit()
    db.refresh(db_label)
    return db_label
@router.get("/{label_id}", response_model=LabelResponse)
def read_label(
    label_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    return _get_label_with_access(label_id, current_user, db)
@router.put("/{label_id}", response_model=LabelResponse)
def update_label(
    label_id: int,
    label_data: LabelUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    label = _get_label_with_access(label_id, current_user, db)
    update_data = label_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(label, field, value)
    db.commit()
    db.refresh(label)
    return label
@router.delete("/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_label(
    label_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> None:
    label = _get_label_with_access(label_id, current_user, db)
    db.delete(label)
    db.commit()
    return None
@router.get("/board/{board_id}", response_model=list[LabelResponse])
def read_labels_by_board(
    board_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    _check_board_access(board_id, current_user, db)
    labels = db.query(Label).filter(Label.board_id == board_id).all()
    return labels
@router.post("/{label_id}/cards/{card_id}", status_code=status.HTTP_200_OK)
def assign_label_to_card(
    label_id: int,
    card_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> dict[str, str]:
    label = _get_label_with_access(label_id, current_user, db)
    card = _get_card_with_access(card_id, current_user, db)
    if label.board_id != card.list.board_id:
        raise HTTPException(status_code=400, detail="Label and card must belong to the same board")
    if label in card.labels:
        raise HTTPException(status_code=400, detail="Label already assigned to this card")
    card.labels.append(label)
    db.commit()
    return {"message": "Label assigned successfully"}
@router.delete("/{label_id}/cards/{card_id}", status_code=status.HTTP_200_OK)
def remove_label_from_card(
    label_id: int,
    card_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> dict[str, str]:
    label = db.query(Label).filter(Label.id == label_id).first()
    if not label:
        raise HTTPException(status_code=404, detail="Label not found")
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    _check_board_access(label.board_id, current_user, db)
    if label.board_id != card.list.board_id:
        raise HTTPException(status_code=400, detail="Label and card must belong to the same board")
    if label not in card.labels:
        raise HTTPException(status_code=400, detail="Label not assigned to this card")
    card.labels.remove(label)
    db.commit()
    return {"message": "Label removed successfully"}