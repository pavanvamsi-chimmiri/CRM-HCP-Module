from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Deal, DealStage


class CRUDDeal(CRUDBase[Deal]):
    async def get_by_owner(
        self,
        db: AsyncSession,
        *,
        deal_id: UUID,
        owner_id: UUID,
    ) -> Deal | None:
        result = await db.get(Deal, deal_id)
        if result and result.owner_id == owner_id:
            return result
        return None

    async def get_multi_by_owner(
        self,
        db: AsyncSession,
        *,
        owner_id: UUID,
        skip: int = 0,
        limit: int = 20,
        stage: DealStage | None = None,
    ) -> list[Deal]:
        filters = [Deal.owner_id == owner_id]
        if stage:
            filters.append(Deal.stage == stage)
        return await self.get_multi(db, skip=skip, limit=limit, filters=filters)

    async def count_by_owner(
        self,
        db: AsyncSession,
        *,
        owner_id: UUID,
        stage: DealStage | None = None,
    ) -> int:
        filters = [Deal.owner_id == owner_id]
        if stage:
            filters.append(Deal.stage == stage)
        return await self.count(db, filters=filters)


deal = CRUDDeal(Deal)
