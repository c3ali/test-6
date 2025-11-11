from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from models import User
from schemas import UserCreate, UserUpdate
from repositories.base import BaseRepository
from utils.exceptions import DuplicateResourceException
class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self, db: Session):
        super().__init__(db, User)
    def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        return self.db.execute(query).scalar_one_or_none()
    def get_by_username(self, username: str) -> User | None:
        query = select(User).where(User.username == username)
        return self.db.execute(query).scalar_one_or_none()
    def exists_by_email(self, email: str) -> bool:
        return self.get_by_email(email) is not None
    def exists_by_username(self, username: str) -> bool:
        return self.get_by_username(username) is not None
    def create_with_password(self, obj_in: UserCreate, hashed_password: str) -> User:
        if self.exists_by_email(obj_in.email):
            raise DuplicateResourceException(f"User with email {obj_in.email} already exists")
        if self.exists_by_username(obj_in.username):
            raise DuplicateResourceException(f"User with username {obj_in.username} already exists")
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=hashed_password,
            full_name=obj_in.full_name
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    def update_last_login(self, user_id: int) -> User | None:
        query = update(User).where(User.id == user_id).values(last_login=datetime.utcnow()).returning(User)
        result = self.db.execute(query).scalar_one_or_none()
        if result:
            self.db.commit()
            self.db.refresh(result)
        return result
    def deactivate(self, user_id: int) -> User | None:
        query = update(User).where(User.id == user_id).values(is_active=False).returning(User)
        result = self.db.execute(query).scalar_one_or_none()
        if result:
            self.db.commit()
            self.db.refresh(result)
        return result
    def get_active_users(self) -> list[User]:
        query = select(User).where(User.is_active.is_(True))
        return list(self.db.execute(query).scalars().all())