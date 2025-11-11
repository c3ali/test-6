from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models import Card, User
from schemas import CardCreate, CardUpdate, CardResponse, CardMove
from services.card_service import CardService
from auth.dependencies import get_current_user
from database import get_db
from utils.exceptions import NotFoundException, PermissionException
router = APIRouter(prefix="/cards", tags=["cards"])
card_service = CardService()
@router.post("/", response_model=CardResponse, status_code=status.HTTP_201_CREATED)
def create_card(
    card_data: CardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return card_service.create_card(db, card_data, current_user)
    except PermissionException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
@router.get("/{card_id}", response_model=CardResponse)
def get_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return card_service.get_card(db, card_id, current_user)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
@router.put("/{card_id}", response_model=CardResponse)
def update_card(
    card_id: int,
    card_data: CardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return card_service.update_card(db, card_id, card_data, current_user)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        card_service.delete_card(db, card_id, current_user)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
@router.post("/{card_id}/move", response_model=CardResponse)
def move_card(
    card_id: int,
    move_data: CardMove,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return card_service.move_card(db, card_id, move_data, current_user)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
@router.post("/{card_id}/assign/{user_id}", response_model=CardResponse)
def assign_user_to_card(
    card_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return card_service.assign_user_to_card(db, card_id, user_id, current_user)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
@router.delete("/{card_id}/assign/{user_id}", response_model=CardResponse)
def unassign_user_from_card(
    card_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return card_service.unassign_user_from_card(db, card_id, user_id, current_user)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
@router.post("/{card_id}/labels/{label_id}", response_model=CardResponse)
def add_label_to_card(
    card_id: int,
    label_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return card_service.add_label_to_card(db, card_id, label_id, current_user)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
@router.delete("/{card_id}/labels/{label_id}", response_model=CardResponse)
def remove_label_from_card(
    card_id: int,
    label_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return card_service.remove_label_from_card(db, card_id, label_id, current_user)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
@router.get("/list/{list_id}", response_model=List[CardResponse])
def get_cards_by_list(
    list_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return card_service.get_cards_by_list(db, list_id, current_user)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
@router.get("/board/{board_id}", response_model=List[CardResponse])
def get_cards_by_board(
    board_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return card_service.get_cards_by_board(db, board_id, current_user)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
@router.get("/user/assigned", response_model=List[CardResponse])
def get_user_assigned_cards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return card_service.get_user_assigned_cards(db, current_user)