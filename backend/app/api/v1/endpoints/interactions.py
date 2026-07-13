from datetime import date
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession
from app.models import InteractionType, Sentiment
from app.schemas.common import Message, PaginatedResponse
from app.schemas.interaction import (
    InteractionCreate,
    InteractionRead,
    InteractionSummarizeRequest,
    InteractionSummarizeResponse,
    InteractionUpdate,
)
from app.services.interaction import interaction_service

router = APIRouter(prefix="/interactions", tags=["Interactions"])


@router.get("/stats")
async def get_interaction_stats(db: DbSession, current_user: CurrentUser) -> dict:
    return await interaction_service.get_stats(db, owner=current_user)


@router.get("", response_model=PaginatedResponse[InteractionRead])
async def list_interactions(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    doctor_name: str | None = Query(default=None),
    interaction_type: InteractionType | None = None,
    sentiment: Sentiment | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> PaginatedResponse[InteractionRead]:
    return await interaction_service.get_multi(
        db,
        owner=current_user,
        skip=skip,
        limit=limit,
        doctor_name=doctor_name,
        interaction_type=interaction_type,
        sentiment=sentiment,
        from_date=from_date,
        to_date=to_date,
    )


@router.post("", response_model=InteractionRead, status_code=status.HTTP_201_CREATED)
async def create_interaction(
    db: DbSession,
    current_user: CurrentUser,
    interaction_in: InteractionCreate,
) -> InteractionRead:
    return await interaction_service.create(db, interaction_in=interaction_in, owner=current_user)


@router.post("/summarize", response_model=InteractionSummarizeResponse)
async def summarize_interaction_notes(
    db: DbSession,
    current_user: CurrentUser,
    body: InteractionSummarizeRequest,
) -> InteractionSummarizeResponse:
    return await interaction_service.summarize_notes(
        db, text=body.text, doctor_name=body.doctor_name, owner=current_user
    )


@router.get("/{interaction_id}", response_model=InteractionRead)
async def get_interaction(
    db: DbSession,
    current_user: CurrentUser,
    interaction_id: UUID,
) -> InteractionRead:
    return await interaction_service.get(db, interaction_id=interaction_id, owner=current_user)


@router.patch("/{interaction_id}", response_model=InteractionRead)
async def update_interaction(
    db: DbSession,
    current_user: CurrentUser,
    interaction_id: UUID,
    interaction_in: InteractionUpdate,
) -> InteractionRead:
    return await interaction_service.update(
        db, interaction_id=interaction_id, interaction_in=interaction_in, owner=current_user
    )


@router.delete("/{interaction_id}", response_model=Message)
async def delete_interaction(
    db: DbSession,
    current_user: CurrentUser,
    interaction_id: UUID,
) -> Message:
    await interaction_service.delete(db, interaction_id=interaction_id, owner=current_user)
    return Message(message="Interaction deleted successfully")
