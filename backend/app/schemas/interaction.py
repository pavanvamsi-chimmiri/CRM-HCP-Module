from datetime import date, time
from uuid import UUID

from pydantic import BaseModel, Field

from app.models import InteractionType, Sentiment
from app.schemas.common import BaseSchema, TimestampSchema


class InteractionBase(BaseSchema):
    doctor_name: str = Field(min_length=1, max_length=255)
    interaction_type: InteractionType
    interaction_date: date
    interaction_time: time
    attendees: str | None = None
    topics: list[str] = Field(default_factory=list)
    materials_shared: str | None = None
    sentiment: Sentiment | None = None
    outcome: str | None = None
    samples: str | None = None
    follow_up: str | None = None
    hcp_id: UUID | None = None


class InteractionCreate(InteractionBase):
    pass


class InteractionUpdate(BaseModel):
    doctor_name: str | None = Field(default=None, max_length=255)
    interaction_type: InteractionType | None = None
    interaction_date: date | None = None
    interaction_time: time | None = None
    attendees: str | None = None
    topics: list[str] | None = None
    materials_shared: str | None = None
    sentiment: Sentiment | None = None
    outcome: str | None = None
    samples: str | None = None
    follow_up: str | None = None


class InteractionSummarizeRequest(BaseModel):
    text: str = Field(min_length=1, description="Voice note or free-text notes to summarize")
    doctor_name: str | None = None


class InteractionSummarizeResponse(BaseModel):
    summary: str
    key_points: list[str] = Field(default_factory=list)
    outcome_highlight: str = ""


class InteractionRead(InteractionBase, TimestampSchema):
    id: UUID
    owner_id: UUID
    hcp_id: UUID


class HCPBase(BaseSchema):
    doctor_name: str = Field(min_length=1, max_length=255)
    specialty: str | None = None
    institution: str | None = None
    email: str | None = None
    phone: str | None = None


class HCPCreate(HCPBase):
    pass


class HCPRead(HCPBase, TimestampSchema):
    id: UUID
    owner_id: UUID
