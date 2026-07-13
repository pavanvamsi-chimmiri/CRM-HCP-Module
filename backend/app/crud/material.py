from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Material


class CRUDMaterial(CRUDBase[Material]):
    async def get_by_owner(
        self,
        db: AsyncSession,
        *,
        material_id: UUID,
        owner_id: UUID,
    ) -> Material | None:
        result = await db.get(Material, material_id)
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
        category: str | None = None,
        active_only: bool = True,
    ) -> list[Material]:
        filters = [Material.owner_id == owner_id]
        if category:
            filters.append(Material.category == category)
        if active_only:
            filters.append(Material.is_active.is_(True))
        return await self.get_multi(db, skip=skip, limit=limit, filters=filters)

    async def count_by_owner(
        self,
        db: AsyncSession,
        *,
        owner_id: UUID,
        category: str | None = None,
        active_only: bool = True,
    ) -> int:
        filters = [Material.owner_id == owner_id]
        if category:
            filters.append(Material.category == category)
        if active_only:
            filters.append(Material.is_active.is_(True))
        return await self.count(db, filters=filters)


material = CRUDMaterial(Material)
