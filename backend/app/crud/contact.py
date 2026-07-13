from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Contact


class CRUDContact(CRUDBase[Contact]):
    async def get_by_owner(
        self,
        db: AsyncSession,
        *,
        contact_id: UUID,
        owner_id: UUID,
    ) -> Contact | None:
        result = await db.get(Contact, contact_id)
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
    ) -> list[Contact]:
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=[Contact.owner_id == owner_id],
        )

    async def count_by_owner(self, db: AsyncSession, *, owner_id: UUID) -> int:
        return await self.count(db, filters=[Contact.owner_id == owner_id])


contact = CRUDContact(Contact)
