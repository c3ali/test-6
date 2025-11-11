from typing import TypeVar, Type, Generic, Optional, Any, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.orm import DeclarativeBase
ModelType = TypeVar("ModelType", bound=DeclarativeBase)
class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        self.model = model
        self.db_session = db_session
    async def get(self, id: Any) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()
    async def get_multi(
        self, skip: int = 0, limit: int = 100, **filters: Any
    ) -> Sequence[ModelType]:
        query = select(self.model)
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)
        query = query.offset(skip).limit(limit)
        result = await self.db_session.execute(query)
        return result.scalars().all()
    async def create(self, obj_in: dict[str, Any]) -> ModelType:
        stmt = insert(self.model).values(**obj_in).returning(self.model)
        result = await self.db_session.execute(stmt)
        await self.db_session.commit()
        return result.scalar_one()
    async def update(self, db_obj: ModelType, obj_in: dict[str, Any]) -> ModelType:
        stmt = (
            update(self.model)
            .where(self.model.id == db_obj.id)
            .values(**obj_in)
            .returning(self.model)
        )
        result = await self.db_session.execute(stmt)
        await self.db_session.commit()
        return result.scalar_one()
    async def delete(self, id: Any) -> Optional[ModelType]:
        stmt = delete(self.model).where(self.model.id == id).returning(self.model)
        result = await self.db_session.execute(stmt)
        await self.db_session.commit()
        return result.scalar_one_or_none()
    async def count(self, **filters: Any) -> int:
        query = select(func.count()).select_from(self.model)
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)
        result = await self.db_session.execute(query)
        return result.scalar()