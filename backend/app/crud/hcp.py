from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models import HCP


class CRUDHCP(CRUDBase[HCP]):
    async def get_by_owner(
        self,
        db: AsyncSession,
        *,
        hcp_id: UUID,
        owner_id: UUID,
    ) -> HCP | None:
        result = await db.get(HCP, hcp_id)
        if result and result.owner_id == owner_id:
            return result
        return None

    async def get_by_doctor_name(
        self,
        db: AsyncSession,
        *,
        doctor_name: str,
        owner_id: UUID,
    ) -> HCP | None:
        result = await db.execute(
            select(HCP).where(HCP.doctor_name == doctor_name, HCP.owner_id == owner_id)
        )
        return result.scalar_one_or_none()

    async def get_multi_by_owner(
        self,
        db: AsyncSession,
        *,
        owner_id: UUID,
        skip: int = 0,
        limit: int = 20,
        specialty: str | None = None,
    ) -> list[HCP]:
        filters = [HCP.owner_id == owner_id]
        if specialty:
            filters.append(HCP.specialty == specialty)
        return await self.get_multi(db, skip=skip, limit=limit, filters=filters)

    async def count_by_owner(
        self,
        db: AsyncSession,
        *,
        owner_id: UUID,
        specialty: str | None = None,
    ) -> int:
        filters = [HCP.owner_id == owner_id]
        if specialty:
            filters.append(HCP.specialty == specialty)
        return await self.count(db, filters=filters)

    async def get_with_interactions(
        self,
        db: AsyncSession,
        *,
        hcp_id: UUID,
        owner_id: UUID,
    ) -> HCP | None:
        result = await db.execute(
            select(HCP)
            .options(selectinload(HCP.interactions))
            .where(HCP.id == hcp_id, HCP.owner_id == owner_id)
        )
        return result.scalar_one_or_none()


hcp = CRUDHCP(HCP)
