from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate, UserUpdate, UserResponse
from database import get_db
from auth.dependencies import get_current_user, get_current_active_user
from repositories.user_repository import UserRepository
from utils.exceptions import NotFoundException, BadRequestException
router = APIRouter(prefix="/users", tags=["users"])
@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user
@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    user_repo = UserRepository(db)
    try:
        user = user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with id {user_id} not found")
        return user
    except Exception as e:
        if isinstance(e, NotFoundException):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_update: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    user_repo = UserRepository(db)
    try:
        update_data = user_update.model_dump(exclude_unset=True)
        if "email" in update_data and update_data["email"] != current_user.email:
            existing_user = user_repo.get_by_email(update_data["email"])
            if existing_user:
                raise BadRequestException("Email already registered")
        updated_user = user_repo.update(current_user.id, update_data)
        if not updated_user:
            raise NotFoundException(f"User with id {current_user.id} not found")
        return updated_user
    except Exception as e:
        if isinstance(e, (NotFoundException, BadRequestException)):
            status_code = status.HTTP_400_BAD_REQUEST if isinstance(e, BadRequestException) else status.HTTP_404_NOT_FOUND
            raise HTTPException(status_code=status_code, detail=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_me(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    user_repo = UserRepository(db)
    try:
        success = user_repo.delete(current_user.id)
        if not success:
            raise NotFoundException(f"User with id {current_user.id} not found")
        return None
    except Exception as e:
        if isinstance(e, NotFoundException):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
@router.get("/", response_model=list[UserResponse])
async def read_users(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    skip: int = 0,
    limit: int = 100
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    user_repo = UserRepository(db)
    try:
        users = user_repo.get_all(skip=skip, limit=limit)
        return users
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    user_repo = UserRepository(db)
    try:
        update_data = user_update.model_dump(exclude_unset=True)
        if "email" in update_data:
            existing_user = user_repo.get_by_email(update_data["email"])
            if existing_user and existing_user.id != user_id:
                raise BadRequestException("Email already registered")
        updated_user = user_repo.update(user_id, update_data)
        if not updated_user:
            raise NotFoundException(f"User with id {user_id} not found")
        return updated_user
    except Exception as e:
        if isinstance(e, (NotFoundException, BadRequestException)):
            status_code = status.HTTP_400_BAD_REQUEST if isinstance(e, BadRequestException) else status.HTTP_404_NOT_FOUND
            raise HTTPException(status_code=status_code, detail=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    user_repo = UserRepository(db)
    try:
        success = user_repo.delete(user_id)
        if not success:
            raise NotFoundException(f"User with id {user_id} not found")
        return None
    except Exception as e:
        if isinstance(e, NotFoundException):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))