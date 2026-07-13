from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, record_id: UUID) -> ModelType | None:
        result = await db.execute(select(self.model).where(self.model.id == record_id))
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 20,
        filters: list[Any] | None = None,
    ) -> list[ModelType]:
        query = select(self.model)
        if filters:
            for condition in filters:
                query = query.where(condition)
        query = query.offset(skip).limit(limit).order_by(self.model.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    async def count(self, db: AsyncSession, filters: list[Any] | None = None) -> int:
        query = select(func.count()).select_from(self.model)
        if filters:
            for condition in filters:
                query = query.where(condition)
        result = await db.execute(query)
        return result.scalar_one()

    async def create(self, db: AsyncSession, *, obj_in: dict[str, Any]) -> ModelType:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: dict[str, Any],
    ) -> ModelType:
        for field, value in obj_in.items():
            if value is not None:
                setattr(db_obj, field, value)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, db_obj: ModelType) -> None:
        await db.delete(db_obj)
        await db.flush()

    def _apply_filters(self, query: Select[tuple[ModelType]], filters: list[Any]) -> Select:
        for condition in filters:
            query = query.where(condition)
        return query
