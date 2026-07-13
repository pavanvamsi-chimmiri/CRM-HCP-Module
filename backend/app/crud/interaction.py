from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models import Interaction, InteractionType, Material, Sentiment
from app.models.associations import interaction_materials


class CRUDInteraction(CRUDBase[Interaction]):
    async def get_by_owner(
        self,
        db: AsyncSession,
        *,
        interaction_id: UUID,
        owner_id: UUID,
    ) -> Interaction | None:
        result = await db.get(Interaction, interaction_id)
        if result and result.owner_id == owner_id:
            return result
        return None

    async def get_with_relations(
        self,
        db: AsyncSession,
        *,
        interaction_id: UUID,
        owner_id: UUID,
    ) -> Interaction | None:
        result = await db.execute(
            select(Interaction)
            .options(
                selectinload(Interaction.materials),
                selectinload(Interaction.followups),
                selectinload(Interaction.hcp),
            )
            .where(Interaction.id == interaction_id, Interaction.owner_id == owner_id)
        )
        return result.scalar_one_or_none()

    async def get_multi_by_owner(
        self,
        db: AsyncSession,
        *,
        owner_id: UUID,
        skip: int = 0,
        limit: int = 20,
        hcp_id: UUID | None = None,
        interaction_type: InteractionType | None = None,
        sentiment: Sentiment | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[Interaction]:
        filters = [Interaction.owner_id == owner_id]
        if hcp_id:
            filters.append(Interaction.hcp_id == hcp_id)
        if interaction_type:
            filters.append(Interaction.interaction_type == interaction_type)
        if sentiment:
            filters.append(Interaction.sentiment == sentiment)
        if from_date:
            filters.append(Interaction.interaction_date >= from_date)
        if to_date:
            filters.append(Interaction.interaction_date <= to_date)
        return await self.get_multi(db, skip=skip, limit=limit, filters=filters)

    async def count_by_owner(
        self,
        db: AsyncSession,
        *,
        owner_id: UUID,
        hcp_id: UUID | None = None,
        interaction_type: InteractionType | None = None,
        sentiment: Sentiment | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> int:
        filters = [Interaction.owner_id == owner_id]
        if hcp_id:
            filters.append(Interaction.hcp_id == hcp_id)
        if interaction_type:
            filters.append(Interaction.interaction_type == interaction_type)
        if sentiment:
            filters.append(Interaction.sentiment == sentiment)
        if from_date:
            filters.append(Interaction.interaction_date >= from_date)
        if to_date:
            filters.append(Interaction.interaction_date <= to_date)
        return await self.count(db, filters=filters)

    async def get_multi_by_hcp(
        self,
        db: AsyncSession,
        *,
        hcp_id: UUID,
        owner_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Interaction]:
        return await self.get_multi_by_owner(
            db, owner_id=owner_id, skip=skip, limit=limit, hcp_id=hcp_id
        )

    async def add_materials(
        self,
        db: AsyncSession,
        *,
        interaction: Interaction,
        material_ids: list[UUID],
    ) -> Interaction:
        if not material_ids:
            return interaction

        result = await db.execute(select(Material).where(Material.id.in_(material_ids)))
        materials = list(result.scalars().all())
        interaction.materials = materials
        await db.flush()
        await db.refresh(interaction, attribute_names=["materials"])
        return interaction

    async def set_materials(
        self,
        db: AsyncSession,
        *,
        interaction: Interaction,
        material_ids: list[UUID],
    ) -> Interaction:
        await db.execute(
            interaction_materials.delete().where(
                interaction_materials.c.interaction_id == interaction.id
            )
        )
        return await self.add_materials(db, interaction=interaction, material_ids=material_ids)


interaction = CRUDInteraction(Interaction)
