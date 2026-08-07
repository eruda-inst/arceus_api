"""column versao_token for user

Revision ID: 7fe6ceec959e
Revises: 562fd3594f91
Create Date: 2026-08-07 08:33:38.460223

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7fe6ceec959e"
down_revision: str | Sequence[str] | None = "562fd3594f91"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        table_name="usuarios",
        column=sa.Column(
            "versao_token",
            type_=sa.Integer,
            default=0,
            server_default="0",
            nullable=False,
            index=False,
            unique=False,
        ),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_column(table_name="usuarios", column_name="versao_token", if_exists=True)
