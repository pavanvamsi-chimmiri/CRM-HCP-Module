from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.common import Message, PaginatedResponse
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate
from app.services.company import company_service

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get("", response_model=PaginatedResponse[CompanyRead])
async def list_companies(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> PaginatedResponse[CompanyRead]:
    return await company_service.get_multi(db, owner=current_user, skip=skip, limit=limit)


@router.post("", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
async def create_company(
    db: DbSession,
    current_user: CurrentUser,
    company_in: CompanyCreate,
) -> CompanyRead:
    return await company_service.create(db, company_in=company_in, owner=current_user)


@router.get("/{company_id}", response_model=CompanyRead)
async def get_company(
    db: DbSession,
    current_user: CurrentUser,
    company_id: UUID,
) -> CompanyRead:
    return await company_service.get(db, company_id=company_id, owner=current_user)


@router.patch("/{company_id}", response_model=CompanyRead)
async def update_company(
    db: DbSession,
    current_user: CurrentUser,
    company_id: UUID,
    company_in: CompanyUpdate,
) -> CompanyRead:
    return await company_service.update(
        db, company_id=company_id, company_in=company_in, owner=current_user
    )


@router.delete("/{company_id}", response_model=Message)
async def delete_company(
    db: DbSession,
    current_user: CurrentUser,
    company_id: UUID,
) -> Message:
    await company_service.delete(db, company_id=company_id, owner=current_user)
    return Message(message="Company deleted successfully")
