from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Message(BaseSchema):
    message: str


class PaginationParams(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseSchema, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int


class TimestampSchema(BaseSchema):
    created_at: datetime
    updated_at: datetime


class IDSchema(BaseSchema):
    id: UUID
