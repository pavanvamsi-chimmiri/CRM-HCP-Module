from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema, TimestampSchema


class CompanyBase(BaseSchema):
    name: str = Field(min_length=1, max_length=255)
    industry: str | None = Field(default=None, max_length=100)
    website: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    address: str | None = None
    description: str | None = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    industry: str | None = Field(default=None, max_length=100)
    website: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    address: str | None = None
    description: str | None = None


class CompanyRead(CompanyBase, TimestampSchema):
    id: UUID
    owner_id: UUID
