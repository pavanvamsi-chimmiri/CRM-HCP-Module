from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models import Followup, FollowupStatus


class CRUDFollowup(CRUDBase[Followup]):
    async def get_by_owner(
        self,
        db: AsyncSession,
        *,
        followup_id: UUID,
        owner_id: UUID,
    ) -> Followup | None:
        result = await db.get(Followup, followup_id)
        if result and result.owner_id == owner_id:
            return result
        return None

    async def get_with_interaction(
        self,
        db: AsyncSession,
        *,
        followup_id: UUID,
        owner_id: UUID,
    ) -> Followup | None:
        result = await db.execute(
            select(Followup)
            .options(selectinload(Followup.interaction))
            .where(Followup.id == followup_id, Followup.owner_id == owner_id)
        )
        return result.scalar_one_or_none()

    async def get_multi_by_owner(
        self,
        db: AsyncSession,
        *,
        owner_id: UUID,
        skip: int = 0,
        limit: int = 20,
        status: FollowupStatus | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[Followup]:
        filters = [Followup.owner_id == owner_id]
        if status:
            filters.append(Followup.status == status)
        if from_date:
            filters.append(Followup.followup_date >= from_date)
        if to_date:
            filters.append(Followup.followup_date <= to_date)
        return await self.get_multi(db, skip=skip, limit=limit, filters=filters)

    async def count_by_owner(
        self,
        db: AsyncSession,
        *,
        owner_id: UUID,
        status: FollowupStatus | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> int:
        filters = [Followup.owner_id == owner_id]
        if status:
            filters.append(Followup.status == status)
        if from_date:
            filters.append(Followup.followup_date >= from_date)
        if to_date:
            filters.append(Followup.followup_date <= to_date)
        return await self.count(db, filters=filters)

    async def get_by_interaction(
        self,
        db: AsyncSession,
        *,
        interaction_id: UUID,
        owner_id: UUID,
    ) -> list[Followup]:
        return await self.get_multi(
            db,
            filters=[
                Followup.interaction_id == interaction_id,
                Followup.owner_id == owner_id,
            ],
        )


followup = CRUDFollowup(Followup)
