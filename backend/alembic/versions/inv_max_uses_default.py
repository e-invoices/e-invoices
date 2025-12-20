"""set invitation max_uses default to 1

Revision ID: set_invitation_max_uses_default
Revises: add_organizations
Create Date: 2025-12-20 16:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "set_invitation_max_uses_default"
down_revision = "add_organizations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Update existing invitations using SQLAlchemy
    organization_invitations = sa.table(
        "organization_invitations",
        sa.column("max_uses", sa.Integer),
        sa.column("use_count", sa.Integer),
        sa.column("is_active", sa.Boolean),
    )

    # Update existing invitations that have NULL max_uses to 1
    op.execute(
        organization_invitations.update()
        .where(organization_invitations.c.max_uses.is_(None))
        .values(max_uses=1)
    )

    # Deactivate any invitations where use_count >= max_uses
    op.execute(
        organization_invitations.update()
        .where(
            sa.and_(
                organization_invitations.c.use_count
                >= organization_invitations.c.max_uses,
                organization_invitations.c.is_active.is_(True),
            )
        )
        .values(is_active=False)
    )

    # Now set the column to NOT NULL with default 1
    op.alter_column(
        "organization_invitations",
        "max_uses",
        existing_type=sa.Integer(),
        nullable=False,
        server_default="1",
    )


def downgrade() -> None:
    # Remove NOT NULL constraint and default value
    op.alter_column(
        "organization_invitations",
        "max_uses",
        existing_type=sa.Integer(),
        nullable=True,
        server_default=None,
    )
