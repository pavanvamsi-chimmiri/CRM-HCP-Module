from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import company as company_crud
from app.crud import contact as contact_crud
from app.models import User
from app.schemas.common import PaginatedResponse
from app.schemas.contact import ContactCreate, ContactRead, ContactUpdate


class ContactService:
    async def _validate_company(self, db: AsyncSession, company_id: UUID | None, owner: User) -> None:
        if company_id is None:
            return
        company = await company_crud.get_by_owner(db, company_id=company_id, owner_id=owner.id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    async def get(self, db: AsyncSession, *, contact_id: UUID, owner: User) -> ContactRead:
        contact = await contact_crud.get_by_owner(db, contact_id=contact_id, owner_id=owner.id)
        if not contact:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
        return ContactRead.model_validate(contact)

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        owner: User,
        skip: int = 0,
        limit: int = 20,
    ) -> PaginatedResponse[ContactRead]:
        contacts = await contact_crud.get_multi_by_owner(
            db, owner_id=owner.id, skip=skip, limit=limit
        )
        total = await contact_crud.count_by_owner(db, owner_id=owner.id)
        return PaginatedResponse[ContactRead](
            items=[ContactRead.model_validate(c) for c in contacts],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def create(
        self,
        db: AsyncSession,
        *,
        contact_in: ContactCreate,
        owner: User,
    ) -> ContactRead:
        await self._validate_company(db, contact_in.company_id, owner)
        data = contact_in.model_dump()
        data["owner_id"] = owner.id
        contact = await contact_crud.create(db, obj_in=data)
        return ContactRead.model_validate(contact)

    async def update(
        self,
        db: AsyncSession,
        *,
        contact_id: UUID,
        contact_in: ContactUpdate,
        owner: User,
    ) -> ContactRead:
        contact = await contact_crud.get_by_owner(db, contact_id=contact_id, owner_id=owner.id)
        if not contact:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

        update_data = contact_in.model_dump(exclude_unset=True)
        if "company_id" in update_data:
            await self._validate_company(db, update_data["company_id"], owner)

        updated = await contact_crud.update(db, db_obj=contact, obj_in=update_data)
        return ContactRead.model_validate(updated)

    async def delete(
        self,
        db: AsyncSession,
        *,
        contact_id: UUID,
        owner: User,
    ) -> None:
        contact = await contact_crud.get_by_owner(db, contact_id=contact_id, owner_id=owner.id)
        if not contact:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
        await contact_crud.delete(db, db_obj=contact)


contact_service = ContactService()
