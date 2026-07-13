from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Company


class CRUDCompany(CRUDBase[Company]):
    async def get_by_owner(
        self,
        db: AsyncSession,
        *,
        company_id: UUID,
        owner_id: UUID,
    ) -> Company | None:
        result = await db.get(Company, company_id)
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
    ) -> list[Company]:
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=[Company.owner_id == owner_id],
        )

    async def count_by_owner(self, db: AsyncSession, *, owner_id: UUID) -> int:
        return await self.count(db, filters=[Company.owner_id == owner_id])


company = CRUDCompany(Company)
