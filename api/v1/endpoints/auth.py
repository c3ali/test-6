from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate, UserResponse, Token, TokenRefresh
from database import get_db
from auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from repositories.user_repository import UserRepository
from utils.validators import validate_email, validate_password
from utils.exceptions import UserAlreadyExistsError, InvalidCredentialsError
router = APIRouter(prefix="/auth", tags=["auth"])
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if not validate_email(user_data.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    if not validate_password(user_data.password):
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    user_repo = UserRepository(db)
    if user_repo.get_by_email(user_data.email):
        raise UserAlreadyExistsError(detail="Email already registered")
    if user_repo.get_by_username(user_data.username):
        raise UserAlreadyExistsError(detail="Username already taken")
    user = user_repo.create(user_data)
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )
@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = user_repo.authenticate(form_data.username, form_data.password)
    if not user:
        raise InvalidCredentialsError(detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )
@router.post("/refresh", response_model=Token)
async def refresh(token_data: TokenRefresh, db: Session = Depends(get_db)):
    payload = verify_token(token_data.refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )