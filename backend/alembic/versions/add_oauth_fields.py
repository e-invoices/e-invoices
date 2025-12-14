"""add oauth fields to users

Revision ID: add_oauth_fields
Revises: 0e8f9682ceca
Create Date: 2025-12-14

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_oauth_fields"
down_revision: Union[str, None] = "0e8f9682ceca"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to users table
    op.add_column("users", sa.Column("auth_provider", sa.String(50), nullable=True))
    op.add_column("users", sa.Column("google_id", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("picture_url", sa.String(500), nullable=True))
    op.add_column("users", sa.Column("is_active", sa.Boolean(), nullable=True))
    op.add_column("users", sa.Column("is_verified", sa.Boolean(), nullable=True))
    op.add_column(
        "users", sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True)
    )

    # Set default values for existing rows
    op.execute("UPDATE users SET auth_provider = 'email' WHERE auth_provider IS NULL")
    op.execute("UPDATE users SET is_active = true WHERE is_active IS NULL")
    op.execute("UPDATE users SET is_verified = false WHERE is_verified IS NULL")

    # Make columns not nullable after setting defaults
    op.alter_column("users", "auth_provider", nullable=False, server_default="email")
    op.alter_column("users", "is_active", nullable=False, server_default="true")
    op.alter_column("users", "is_verified", nullable=False, server_default="false")

    # Make hashed_password nullable (for OAuth users)
    op.alter_column("users", "hashed_password", nullable=True)

    # Create index on google_id
    op.create_index("ix_users_google_id", "users", ["google_id"], unique=True)


def downgrade() -> None:
    # Remove index
    op.drop_index("ix_users_google_id", table_name="users")

    # Make hashed_password not nullable again
    op.alter_column("users", "hashed_password", nullable=False)

    # Remove new columns
    op.drop_column("users", "last_login_at")
    op.drop_column("users", "is_verified")
    op.drop_column("users", "is_active")
    op.drop_column("users", "picture_url")
    op.drop_column("users", "google_id")
    op.drop_column("users", "auth_provider")
