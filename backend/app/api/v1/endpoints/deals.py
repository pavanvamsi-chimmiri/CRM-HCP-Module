from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession
from app.models import DealStage
from app.schemas.common import Message, PaginatedResponse
from app.schemas.deal import DealCreate, DealRead, DealUpdate
from app.services.deal import deal_service

router = APIRouter(prefix="/deals", tags=["Deals"])


@router.get("", response_model=PaginatedResponse[DealRead])
async def list_deals(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    stage: DealStage | None = None,
) -> PaginatedResponse[DealRead]:
    return await deal_service.get_multi(
        db, owner=current_user, skip=skip, limit=limit, stage=stage
    )


@router.post("", response_model=DealRead, status_code=status.HTTP_201_CREATED)
async def create_deal(
    db: DbSession,
    current_user: CurrentUser,
    deal_in: DealCreate,
) -> DealRead:
    return await deal_service.create(db, deal_in=deal_in, owner=current_user)


@router.get("/{deal_id}", response_model=DealRead)
async def get_deal(
    db: DbSession,
    current_user: CurrentUser,
    deal_id: UUID,
) -> DealRead:
    return await deal_service.get(db, deal_id=deal_id, owner=current_user)


@router.patch("/{deal_id}", response_model=DealRead)
async def update_deal(
    db: DbSession,
    current_user: CurrentUser,
    deal_id: UUID,
    deal_in: DealUpdate,
) -> DealRead:
    return await deal_service.update(
        db, deal_id=deal_id, deal_in=deal_in, owner=current_user
    )


@router.delete("/{deal_id}", response_model=Message)
async def delete_deal(
    db: DbSession,
    current_user: CurrentUser,
    deal_id: UUID,
) -> Message:
    await deal_service.delete(db, deal_id=deal_id, owner=current_user)
    return Message(message="Deal deleted successfully")
