from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models import DealStage
from app.schemas.common import BaseSchema, TimestampSchema


class DealBase(BaseSchema):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    value: Decimal = Field(default=Decimal("0.00"), ge=0)
    stage: DealStage = DealStage.LEAD
    expected_close_date: date | None = None
    company_id: UUID | None = None
    contact_id: UUID | None = None


class DealCreate(DealBase):
    pass


class DealUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    value: Decimal | None = Field(default=None, ge=0)
    stage: DealStage | None = None
    expected_close_date: date | None = None
    company_id: UUID | None = None
    contact_id: UUID | None = None


class DealRead(DealBase, TimestampSchema):
    id: UUID
    owner_id: UUID
