from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.common import Message, PaginatedResponse
from app.schemas.contact import ContactCreate, ContactRead, ContactUpdate
from app.services.contact import contact_service

router = APIRouter(prefix="/contacts", tags=["Contacts"])


@router.get("", response_model=PaginatedResponse[ContactRead])
async def list_contacts(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> PaginatedResponse[ContactRead]:
    return await contact_service.get_multi(db, owner=current_user, skip=skip, limit=limit)


@router.post("", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
async def create_contact(
    db: DbSession,
    current_user: CurrentUser,
    contact_in: ContactCreate,
) -> ContactRead:
    return await contact_service.create(db, contact_in=contact_in, owner=current_user)


@router.get("/{contact_id}", response_model=ContactRead)
async def get_contact(
    db: DbSession,
    current_user: CurrentUser,
    contact_id: UUID,
) -> ContactRead:
    return await contact_service.get(db, contact_id=contact_id, owner=current_user)


@router.patch("/{contact_id}", response_model=ContactRead)
async def update_contact(
    db: DbSession,
    current_user: CurrentUser,
    contact_id: UUID,
    contact_in: ContactUpdate,
) -> ContactRead:
    return await contact_service.update(
        db, contact_id=contact_id, contact_in=contact_in, owner=current_user
    )


@router.delete("/{contact_id}", response_model=Message)
async def delete_contact(
    db: DbSession,
    current_user: CurrentUser,
    contact_id: UUID,
) -> Message:
    await contact_service.delete(db, contact_id=contact_id, owner=current_user)
    return Message(message="Contact deleted successfully")
