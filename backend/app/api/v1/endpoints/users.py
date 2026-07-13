from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, DbSession, SuperUser
from app.schemas.common import Message, PaginatedResponse
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.user import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=PaginatedResponse[UserRead])
async def list_users(
    db: DbSession,
    _: SuperUser,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> PaginatedResponse[UserRead]:
    return await user_service.get_multi(db, skip=skip, limit=limit)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(db: DbSession, _: SuperUser, user_in: UserCreate) -> UserRead:
    return await user_service.create(db, user_in)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(db: DbSession, user_id: UUID, current_user: CurrentUser) -> UserRead:
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")
    return await user_service.get(db, user_id)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    db: DbSession,
    user_id: UUID,
    user_in: UserUpdate,
    current_user: CurrentUser,
) -> UserRead:
    return await user_service.update(db, user_id=user_id, user_in=user_in, current_user=current_user)


@router.delete("/{user_id}", response_model=Message)
async def delete_user(db: DbSession, user_id: UUID, current_user: SuperUser) -> Message:
    await user_service.delete(db, user_id=user_id, current_user=current_user)
    return Message(message="User deleted successfully")
