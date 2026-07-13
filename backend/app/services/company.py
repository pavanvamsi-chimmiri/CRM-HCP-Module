from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import company as company_crud
from app.models import User
from app.schemas.common import PaginatedResponse
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate


class CompanyService:
    async def get(self, db: AsyncSession, *, company_id: UUID, owner: User) -> CompanyRead:
        company = await company_crud.get_by_owner(db, company_id=company_id, owner_id=owner.id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        return CompanyRead.model_validate(company)

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        owner: User,
        skip: int = 0,
        limit: int = 20,
    ) -> PaginatedResponse[CompanyRead]:
        companies = await company_crud.get_multi_by_owner(
            db, owner_id=owner.id, skip=skip, limit=limit
        )
        total = await company_crud.count_by_owner(db, owner_id=owner.id)
        return PaginatedResponse[CompanyRead](
            items=[CompanyRead.model_validate(c) for c in companies],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def create(
        self,
        db: AsyncSession,
        *,
        company_in: CompanyCreate,
        owner: User,
    ) -> CompanyRead:
        data = company_in.model_dump()
        data["owner_id"] = owner.id
        company = await company_crud.create(db, obj_in=data)
        return CompanyRead.model_validate(company)

    async def update(
        self,
        db: AsyncSession,
        *,
        company_id: UUID,
        company_in: CompanyUpdate,
        owner: User,
    ) -> CompanyRead:
        company = await company_crud.get_by_owner(db, company_id=company_id, owner_id=owner.id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

        updated = await company_crud.update(
            db,
            db_obj=company,
            obj_in=company_in.model_dump(exclude_unset=True),
        )
        return CompanyRead.model_validate(updated)

    async def delete(
        self,
        db: AsyncSession,
        *,
        company_id: UUID,
        owner: User,
    ) -> None:
        company = await company_crud.get_by_owner(db, company_id=company_id, owner_id=owner.id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        await company_crud.delete(db, db_obj=company)


company_service = CompanyService()
