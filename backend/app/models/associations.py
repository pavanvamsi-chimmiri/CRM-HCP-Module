from sqlalchemy import Column, ForeignKey, Integer, Table, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.db.base import Base

interaction_materials = Table(
    "interaction_materials",
    Base.metadata,
    Column(
        "interaction_id",
        PGUUID(as_uuid=True),
        ForeignKey("interactions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "material_id",
        PGUUID(as_uuid=True),
        ForeignKey("materials.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("quantity", Integer, default=1, nullable=False),
    Column("notes", Text, nullable=True),
)
