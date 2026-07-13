"""HCP module schema migration

Revision ID: 002
Revises: 001
Create Date: 2026-07-13

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop legacy generic CRM tables
    op.drop_index("ix_deals_title", table_name="deals")
    op.drop_index("ix_deals_stage", table_name="deals")
    op.drop_index("ix_deals_owner_id", table_name="deals")
    op.drop_index("ix_deals_contact_id", table_name="deals")
    op.drop_index("ix_deals_company_id", table_name="deals")
    op.drop_table("deals")

    op.drop_index("ix_contacts_owner_id", table_name="contacts")
    op.drop_index("ix_contacts_email", table_name="contacts")
    op.drop_index("ix_contacts_company_id", table_name="contacts")
    op.drop_table("contacts")

    op.drop_index("ix_companies_owner_id", table_name="companies")
    op.drop_index("ix_companies_name", table_name="companies")
    op.drop_table("companies")

    op.execute("DROP TYPE IF EXISTS deal_stage")

    # Create HCP module enums
    interaction_type = postgresql.ENUM(
        "in_person",
        "phone_call",
        "video_call",
        "email",
        "conference",
        "other",
        name="interaction_type",
        create_type=False,
    )
    sentiment = postgresql.ENUM(
        "positive",
        "neutral",
        "negative",
        "mixed",
        name="sentiment",
        create_type=False,
    )
    followup_status = postgresql.ENUM(
        "pending",
        "completed",
        "cancelled",
        "overdue",
        name="followup_status",
        create_type=False,
    )

    op.execute(
        "CREATE TYPE interaction_type AS ENUM "
        "('in_person', 'phone_call', 'video_call', 'email', 'conference', 'other')"
    )
    op.execute(
        "CREATE TYPE sentiment AS ENUM ('positive', 'neutral', 'negative', 'mixed')"
    )
    op.execute(
        "CREATE TYPE followup_status AS ENUM ('pending', 'completed', 'cancelled', 'overdue')"
    )

    # HCP table
    op.create_table(
        "hcp",
        sa.Column("doctor_name", sa.String(length=255), nullable=False),
        sa.Column("specialty", sa.String(length=150), nullable=True),
        sa.Column("institution", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_hcp_doctor_name"), "hcp", ["doctor_name"], unique=False)
    op.create_index(op.f("ix_hcp_owner_id"), "hcp", ["owner_id"], unique=False)
    op.create_index(op.f("ix_hcp_specialty"), "hcp", ["specialty"], unique=False)

    # Materials table
    op.create_table(
        "materials",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_materials_category"), "materials", ["category"], unique=False)
    op.create_index(op.f("ix_materials_name"), "materials", ["name"], unique=False)
    op.create_index(op.f("ix_materials_owner_id"), "materials", ["owner_id"], unique=False)

    # Interactions table
    op.create_table(
        "interactions",
        sa.Column("hcp_id", sa.UUID(), nullable=False),
        sa.Column("doctor_name", sa.String(length=255), nullable=False),
        sa.Column("interaction_type", interaction_type, nullable=False),
        sa.Column("interaction_date", sa.Date(), nullable=False),
        sa.Column("interaction_time", sa.Time(), nullable=False),
        sa.Column("topics", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("sentiment", sentiment, nullable=True),
        sa.Column("outcome", sa.Text(), nullable=True),
        sa.Column("samples", sa.Text(), nullable=True),
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["hcp_id"], ["hcp.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_interactions_doctor_name"), "interactions", ["doctor_name"], unique=False
    )
    op.create_index(
        op.f("ix_interactions_hcp_id"), "interactions", ["hcp_id"], unique=False
    )
    op.create_index(
        op.f("ix_interactions_interaction_date"),
        "interactions",
        ["interaction_date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_interactions_interaction_type"),
        "interactions",
        ["interaction_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_interactions_owner_id"), "interactions", ["owner_id"], unique=False
    )
    op.create_index(
        op.f("ix_interactions_sentiment"), "interactions", ["sentiment"], unique=False
    )

    # Interaction-Materials association
    op.create_table(
        "interaction_materials",
        sa.Column("interaction_id", sa.UUID(), nullable=False),
        sa.Column("material_id", sa.UUID(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["interaction_id"], ["interactions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["material_id"], ["materials.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("interaction_id", "material_id"),
    )

    # Followups table
    op.create_table(
        "followups",
        sa.Column("interaction_id", sa.UUID(), nullable=False),
        sa.Column("followup_date", sa.Date(), nullable=False),
        sa.Column("followup_time", sa.Time(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", followup_status, nullable=False),
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["interaction_id"], ["interactions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_followups_followup_date"), "followups", ["followup_date"], unique=False
    )
    op.create_index(
        op.f("ix_followups_interaction_id"), "followups", ["interaction_id"], unique=False
    )
    op.create_index(op.f("ix_followups_owner_id"), "followups", ["owner_id"], unique=False)
    op.create_index(op.f("ix_followups_status"), "followups", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_followups_status"), table_name="followups")
    op.drop_index(op.f("ix_followups_owner_id"), table_name="followups")
    op.drop_index(op.f("ix_followups_interaction_id"), table_name="followups")
    op.drop_index(op.f("ix_followups_followup_date"), table_name="followups")
    op.drop_table("followups")

    op.drop_table("interaction_materials")

    op.drop_index(op.f("ix_interactions_sentiment"), table_name="interactions")
    op.drop_index(op.f("ix_interactions_owner_id"), table_name="interactions")
    op.drop_index(op.f("ix_interactions_interaction_type"), table_name="interactions")
    op.drop_index(op.f("ix_interactions_interaction_date"), table_name="interactions")
    op.drop_index(op.f("ix_interactions_hcp_id"), table_name="interactions")
    op.drop_index(op.f("ix_interactions_doctor_name"), table_name="interactions")
    op.drop_table("interactions")

    op.drop_index(op.f("ix_materials_owner_id"), table_name="materials")
    op.drop_index(op.f("ix_materials_name"), table_name="materials")
    op.drop_index(op.f("ix_materials_category"), table_name="materials")
    op.drop_table("materials")

    op.drop_index(op.f("ix_hcp_specialty"), table_name="hcp")
    op.drop_index(op.f("ix_hcp_owner_id"), table_name="hcp")
    op.drop_index(op.f("ix_hcp_doctor_name"), table_name="hcp")
    op.drop_table("hcp")

    op.execute("DROP TYPE IF EXISTS followup_status")
    op.execute("DROP TYPE IF EXISTS sentiment")
    op.execute("DROP TYPE IF EXISTS interaction_type")

    # Restore legacy CRM tables
    op.execute(
        "CREATE TYPE deal_stage AS ENUM "
        "('lead', 'qualified', 'proposal', 'negotiation', 'closed_won', 'closed_lost')"
    )

    op.create_table(
        "companies",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("industry", sa.String(length=100), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_companies_name"), "companies", ["name"], unique=False)
    op.create_index(op.f("ix_companies_owner_id"), "companies", ["owner_id"], unique=False)

    op.create_table(
        "contacts",
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("title", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("company_id", sa.UUID(), nullable=True),
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", "owner_id", name="uq_contact_email_owner"),
    )
    op.create_index(op.f("ix_contacts_company_id"), "contacts", ["company_id"], unique=False)
    op.create_index(op.f("ix_contacts_email"), "contacts", ["email"], unique=False)
    op.create_index(op.f("ix_contacts_owner_id"), "contacts", ["owner_id"], unique=False)

    op.create_table(
        "deals",
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("value", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column(
            "stage",
            sa.Enum(
                "lead",
                "qualified",
                "proposal",
                "negotiation",
                "closed_won",
                "closed_lost",
                name="deal_stage",
            ),
            nullable=False,
        ),
        sa.Column("expected_close_date", sa.Date(), nullable=True),
        sa.Column("company_id", sa.UUID(), nullable=True),
        sa.Column("contact_id", sa.UUID(), nullable=True),
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["contact_id"], ["contacts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_deals_company_id"), "deals", ["company_id"], unique=False)
    op.create_index(op.f("ix_deals_contact_id"), "deals", ["contact_id"], unique=False)
    op.create_index(op.f("ix_deals_owner_id"), "deals", ["owner_id"], unique=False)
    op.create_index(op.f("ix_deals_stage"), "deals", ["stage"], unique=False)
    op.create_index(op.f("ix_deals_title"), "deals", ["title"], unique=False)
