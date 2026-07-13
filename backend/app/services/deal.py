from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import company as company_crud
from app.crud import contact as contact_crud
from app.crud import deal as deal_crud
from app.models import DealStage, User
from app.schemas.common import PaginatedResponse
from app.schemas.deal import DealCreate, DealRead, DealUpdate


class DealService:
    async def _validate_relations(
        self,
        db: AsyncSession,
        *,
        company_id: UUID | None,
        contact_id: UUID | None,
        owner: User,
    ) -> None:
        if company_id:
            company = await company_crud.get_by_owner(
                db, company_id=company_id, owner_id=owner.id
            )
            if not company:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Company not found",
                )
        if contact_id:
            contact = await contact_crud.get_by_owner(
                db, contact_id=contact_id, owner_id=owner.id
            )
            if not contact:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Contact not found",
                )

    async def get(self, db: AsyncSession, *, deal_id: UUID, owner: User) -> DealRead:
        deal = await deal_crud.get_by_owner(db, deal_id=deal_id, owner_id=owner.id)
        if not deal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")
        return DealRead.model_validate(deal)

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        owner: User,
        skip: int = 0,
        limit: int = 20,
        stage: DealStage | None = None,
    ) -> PaginatedResponse[DealRead]:
        deals = await deal_crud.get_multi_by_owner(
            db, owner_id=owner.id, skip=skip, limit=limit, stage=stage
        )
        total = await deal_crud.count_by_owner(db, owner_id=owner.id, stage=stage)
        return PaginatedResponse[DealRead](
            items=[DealRead.model_validate(d) for d in deals],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def create(
        self,
        db: AsyncSession,
        *,
        deal_in: DealCreate,
        owner: User,
    ) -> DealRead:
        await self._validate_relations(
            db,
            company_id=deal_in.company_id,
            contact_id=deal_in.contact_id,
            owner=owner,
        )
        data = deal_in.model_dump()
        data["owner_id"] = owner.id
        deal = await deal_crud.create(db, obj_in=data)
        return DealRead.model_validate(deal)

    async def update(
        self,
        db: AsyncSession,
        *,
        deal_id: UUID,
        deal_in: DealUpdate,
        owner: User,
    ) -> DealRead:
        deal = await deal_crud.get_by_owner(db, deal_id=deal_id, owner_id=owner.id)
        if not deal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")

        update_data = deal_in.model_dump(exclude_unset=True)
        company_id = update_data.get("company_id", deal.company_id)
        contact_id = update_data.get("contact_id", deal.contact_id)
        await self._validate_relations(
            db,
            company_id=company_id,
            contact_id=contact_id,
            owner=owner,
        )

        updated = await deal_crud.update(db, db_obj=deal, obj_in=update_data)
        return DealRead.model_validate(updated)

    async def delete(
        self,
        db: AsyncSession,
        *,
        deal_id: UUID,
        owner: User,
    ) -> None:
        deal = await deal_crud.get_by_owner(db, deal_id=deal_id, owner_id=owner.id)
        if not deal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")
        await deal_crud.delete(db, db_obj=deal)


deal_service = DealService()
