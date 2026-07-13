from __future__ import annotations

import enum
from datetime import date, time
from uuid import UUID

from sqlalchemy import Date, Enum, ForeignKey, Text, Time
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class FollowupStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class Followup(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Scheduled follow-up action linked to an interaction."""

    __tablename__ = "followups"

    interaction_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("interactions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    followup_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    followup_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[FollowupStatus] = mapped_column(
        Enum(FollowupStatus, name="followup_status"),
        default=FollowupStatus.PENDING,
        nullable=False,
        index=True,
    )
    owner_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    interaction: Mapped[Interaction] = relationship(back_populates="followups")
    owner: Mapped[User] = relationship(back_populates="followups")
