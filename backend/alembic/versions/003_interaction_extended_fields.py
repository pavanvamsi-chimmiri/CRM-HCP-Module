"""Add extended interaction fields

Revision ID: 003
Revises: 002
Create Date: 2026-07-13

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("interactions", sa.Column("attendees", sa.Text(), nullable=True))
    op.add_column("interactions", sa.Column("materials_shared", sa.Text(), nullable=True))
    op.add_column("interactions", sa.Column("follow_up", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("interactions", "follow_up")
    op.drop_column("interactions", "materials_shared")
    op.drop_column("interactions", "attendees")
