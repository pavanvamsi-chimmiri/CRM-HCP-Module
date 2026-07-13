from datetime import date
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.groq_service import SummarizeRequest, get_groq_service
from app.crud import hcp as hcp_crud
from app.crud import interaction as interaction_crud
from app.models import InteractionType, Sentiment, User
from app.schemas.common import PaginatedResponse
from app.schemas.interaction import (
    InteractionCreate,
    InteractionRead,
    InteractionSummarizeResponse,
    InteractionUpdate,
)


class InteractionService:
    async def _resolve_hcp(
        self,
        db: AsyncSession,
        *,
        doctor_name: str,
        owner: User,
    ) -> UUID:
        existing = await hcp_crud.get_by_doctor_name(
            db, doctor_name=doctor_name, owner_id=owner.id
        )
        if existing:
            return existing.id
        created = await hcp_crud.create(
            db,
            obj_in={"doctor_name": doctor_name, "owner_id": owner.id},
        )
        return created.id

    async def get(
        self,
        db: AsyncSession,
        *,
        interaction_id: UUID,
        owner: User,
    ) -> InteractionRead:
        interaction = await interaction_crud.get_by_owner(
            db, interaction_id=interaction_id, owner_id=owner.id
        )
        if not interaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interaction not found")
        return InteractionRead.model_validate(interaction)

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        owner: User,
        skip: int = 0,
        limit: int = 20,
        doctor_name: str | None = None,
        interaction_type: InteractionType | None = None,
        sentiment: Sentiment | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> PaginatedResponse[InteractionRead]:
        hcp_id = None
        if doctor_name:
            hcp = await hcp_crud.get_by_doctor_name(
                db, doctor_name=doctor_name, owner_id=owner.id
            )
            if hcp:
                hcp_id = hcp.id

        interactions = await interaction_crud.get_multi_by_owner(
            db,
            owner_id=owner.id,
            skip=skip,
            limit=limit,
            hcp_id=hcp_id,
            interaction_type=interaction_type,
            sentiment=sentiment,
            from_date=from_date,
            to_date=to_date,
        )

        if doctor_name and not hcp_id:
            needle = doctor_name.lower()
            interactions = [i for i in interactions if needle in i.doctor_name.lower()]

        total = await interaction_crud.count_by_owner(
            db,
            owner_id=owner.id,
            hcp_id=hcp_id,
            interaction_type=interaction_type,
            sentiment=sentiment,
            from_date=from_date,
            to_date=to_date,
        )

        return PaginatedResponse[InteractionRead](
            items=[InteractionRead.model_validate(i) for i in interactions],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def create(
        self,
        db: AsyncSession,
        *,
        interaction_in: InteractionCreate,
        owner: User,
    ) -> InteractionRead:
        hcp_id = interaction_in.hcp_id or await self._resolve_hcp(
            db, doctor_name=interaction_in.doctor_name, owner=owner
        )
        data = interaction_in.model_dump(exclude={"hcp_id"})
        data["hcp_id"] = hcp_id
        data["owner_id"] = owner.id
        interaction = await interaction_crud.create(db, obj_in=data)
        return InteractionRead.model_validate(interaction)

    async def update(
        self,
        db: AsyncSession,
        *,
        interaction_id: UUID,
        interaction_in: InteractionUpdate,
        owner: User,
    ) -> InteractionRead:
        interaction = await interaction_crud.get_by_owner(
            db, interaction_id=interaction_id, owner_id=owner.id
        )
        if not interaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interaction not found")

        updated = await interaction_crud.update(
            db,
            db_obj=interaction,
            obj_in=interaction_in.model_dump(exclude_unset=True),
        )
        return InteractionRead.model_validate(updated)

    async def delete(self, db: AsyncSession, *, interaction_id: UUID, owner: User) -> None:
        interaction = await interaction_crud.get_by_owner(
            db, interaction_id=interaction_id, owner_id=owner.id
        )
        if not interaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interaction not found")
        await interaction_crud.delete(db, db_obj=interaction)

    async def get_stats(self, db: AsyncSession, *, owner: User) -> dict:
        total = await interaction_crud.count_by_owner(db, owner_id=owner.id)
        positive = await interaction_crud.count_by_owner(
            db, owner_id=owner.id, sentiment=Sentiment.POSITIVE
        )
        pending_followups = 0
        return {
            "total_interactions": total,
            "positive_sentiment": positive,
            "pending_followups": pending_followups,
            "this_month": total,
        }

    async def summarize_notes(
        self,
        db: AsyncSession,
        *,
        text: str,
        doctor_name: str | None,
        owner: User,
    ) -> InteractionSummarizeResponse:
        groq = get_groq_service()
        result = groq.summarize(
            SummarizeRequest(
                text=text,
                doctor_name=doctor_name or "Unknown",
                interaction_type="unknown",
                interaction_date="unknown",
                topics=[],
                sentiment="unknown",
                outcome=None,
                samples=None,
            )
        )
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=result.message or "Failed to summarize voice note",
            )
        return InteractionSummarizeResponse(
            summary=result.summary,
            key_points=result.key_points,
            outcome_highlight=result.outcome_highlight,
        )


interaction_service = InteractionService()
