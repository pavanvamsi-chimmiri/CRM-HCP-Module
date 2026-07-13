from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import BaseSchema, TimestampSchema


class ContactBase(BaseSchema):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    title: str | None = Field(default=None, max_length=100)
    notes: str | None = None
    company_id: UUID | None = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    title: str | None = Field(default=None, max_length=100)
    notes: str | None = None
    company_id: UUID | None = None


class ContactRead(ContactBase, TimestampSchema):
    id: UUID
    owner_id: UUID
