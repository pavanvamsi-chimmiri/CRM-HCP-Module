from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, DbSession
from app.schemas.token import LoginRequest, RefreshTokenRequest, Token
from app.schemas.user import UserCreate, UserRead
from app.services.auth import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserRead, status_code=201)
async def register(db: DbSession, user_in: UserCreate) -> UserRead:
    return await auth_service.register(db, user_in)


@router.post("/login", response_model=Token)
async def login(
    db: DbSession,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await auth_service.authenticate(db, form_data.username, form_data.password)
    return auth_service.create_tokens(user)


@router.post("/login/json", response_model=Token)
async def login_json(db: DbSession, credentials: LoginRequest) -> Token:
    user = await auth_service.authenticate(db, credentials.email, credentials.password)
    return auth_service.create_tokens(user)


@router.post("/refresh", response_model=Token)
async def refresh_token(db: DbSession, body: RefreshTokenRequest) -> Token:
    return await auth_service.refresh_access_token(db, body.refresh_token)


@router.get("/me", response_model=UserRead)
async def get_me(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)
