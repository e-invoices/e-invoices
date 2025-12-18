"""add organizations and invitations

Revision ID: add_organizations
Revises: add_oauth_fields
Create Date: 2025-12-17 10:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "add_organizations"
down_revision = "add_oauth_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create organizations table
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("registration_name", sa.String(length=255), nullable=False),
        sa.Column("edb", sa.String(length=13), nullable=False),
        sa.Column("embs", sa.String(length=20), nullable=False),
        sa.Column("vat_registered", sa.Boolean(), nullable=False, default=True),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("contact_person", sa.String(length=255), nullable=False),
        sa.Column("contact_email", sa.String(length=255), nullable=False),
        sa.Column("contact_phone", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_organizations_id"), "organizations", ["id"], unique=False)
    op.create_index(op.f("ix_organizations_edb"), "organizations", ["edb"], unique=True)

    # Create user_organizations table (many-to-many with role)
    op.create_table(
        "user_organizations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column(
            "role",
            sa.Enum(
                "owner",
                "admin",
                "accountant",
                "member",
                "viewer",
                name="organizationrole",
            ),
            nullable=False,
            default="member",
        ),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("invited_by", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["invited_by"],
            ["users.id"],
            ondelete="SET NULL",
        ),
    )
    op.create_index(
        op.f("ix_user_organizations_id"), "user_organizations", ["id"], unique=False
    )
    op.create_index(
        "ix_user_organizations_user_org",
        "user_organizations",
        ["user_id", "organization_id"],
        unique=True,
    )

    # Create organization_invitations table
    op.create_table(
        "organization_invitations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("target_email", sa.String(length=255), nullable=True),
        sa.Column(
            "role",
            sa.Enum(
                "owner",
                "admin",
                "accountant",
                "member",
                "viewer",
                name="organizationrole",
            ),
            nullable=False,
            default="member",
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("max_uses", sa.Integer(), nullable=True),
        sa.Column("use_count", sa.Integer(), nullable=False, default=0),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        op.f("ix_organization_invitations_id"),
        "organization_invitations",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_organization_invitations_code"),
        "organization_invitations",
        ["code"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_organization_invitations_code"), table_name="organization_invitations"
    )
    op.drop_index(
        op.f("ix_organization_invitations_id"), table_name="organization_invitations"
    )
    op.drop_table("organization_invitations")

    op.drop_index("ix_user_organizations_user_org", table_name="user_organizations")
    op.drop_index(op.f("ix_user_organizations_id"), table_name="user_organizations")
    op.drop_table("user_organizations")

    op.drop_index(op.f("ix_organizations_edb"), table_name="organizations")
    op.drop_index(op.f("ix_organizations_id"), table_name="organizations")
    op.drop_table("organizations")

    # Drop the enum type
    op.execute("DROP TYPE IF EXISTS organizationrole")
