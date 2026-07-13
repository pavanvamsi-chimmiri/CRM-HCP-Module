from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.crud import user as user_crud
from app.models import User
from app.schemas.common import PaginatedResponse
from app.schemas.user import UserCreate, UserRead, UserUpdate


class UserService:
    async def get(self, db: AsyncSession, user_id: UUID) -> UserRead:
        user = await user_crud.get(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return UserRead.model_validate(user)

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 20,
    ) -> PaginatedResponse[UserRead]:
        users = await user_crud.get_multi(db, skip=skip, limit=limit)
        total = await user_crud.count(db)
        return PaginatedResponse[UserRead](
            items=[UserRead.model_validate(u) for u in users],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def create(self, db: AsyncSession, user_in: UserCreate) -> UserRead:
        existing = await user_crud.get_by_email(db, user_in.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        data = user_in.model_dump(exclude={"password"})
        data["hashed_password"] = get_password_hash(user_in.password)
        user = await user_crud.create(db, obj_in=data)
        return UserRead.model_validate(user)

    async def update(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        user_in: UserUpdate,
        current_user: User,
    ) -> UserRead:
        user = await user_crud.get(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if user.id != current_user.id and not current_user.is_superuser:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        if "is_active" in update_data and not current_user.is_superuser:
            update_data.pop("is_active")

        updated = await user_crud.update(db, db_obj=user, obj_in=update_data)
        return UserRead.model_validate(updated)

    async def delete(self, db: AsyncSession, *, user_id: UUID, current_user: User) -> None:
        if not current_user.is_superuser:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        user = await user_crud.get(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account",
            )

        await user_crud.delete(db, db_obj=user)


user_service = UserService()
