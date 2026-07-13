from __future__ import annotations

import enum
from datetime import date, time
from uuid import UUID

from sqlalchemy import Date, Enum, ForeignKey, String, Text, Time
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.associations import interaction_materials


class InteractionType(str, enum.Enum):
    IN_PERSON = "in_person"
    PHONE_CALL = "phone_call"
    VIDEO_CALL = "video_call"
    EMAIL = "email"
    CONFERENCE = "conference"
    OTHER = "other"


class Sentiment(str, enum.Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    MIXED = "mixed"


class Interaction(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """HCP interaction log with full visit/call details."""

    __tablename__ = "interactions"

    hcp_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("hcp.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    doctor_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    interaction_type: Mapped[InteractionType] = mapped_column(
        Enum(InteractionType, name="interaction_type"),
        nullable=False,
        index=True,
    )
    interaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    interaction_time: Mapped[time] = mapped_column(Time, nullable=False)
    topics: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    sentiment: Mapped[Sentiment | None] = mapped_column(
        Enum(Sentiment, name="sentiment"),
        nullable=True,
        index=True,
    )
    attendees: Mapped[str | None] = mapped_column(Text, nullable=True)
    materials_shared: Mapped[str | None] = mapped_column(Text, nullable=True)
    outcome: Mapped[str | None] = mapped_column(Text, nullable=True)
    samples: Mapped[str | None] = mapped_column(Text, nullable=True)
    follow_up: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    hcp: Mapped[HCP] = relationship(back_populates="interactions")
    owner: Mapped[User] = relationship(back_populates="interactions")
    materials: Mapped[list[Material]] = relationship(
        secondary=interaction_materials,
        back_populates="interactions",
    )
    followups: Mapped[list[Followup]] = relationship(
        back_populates="interaction",
        cascade="all, delete-orphan",
    )
