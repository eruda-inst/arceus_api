"""column domain has been dropped

Revision ID: 6b71b98c1b99
Revises: ee16933c1ce4
Create Date: 2026-07-20 15:48:22.080553

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6b71b98c1b99"
down_revision: str | Sequence[str] | None = "ee16933c1ce4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_column(table_name="logs", column_name="dominio", if_exists=True)


def downgrade() -> None:
    op.add_column(
        table_name="logs",
        column=sa.Column("dominio", sa.String(), nullable=False),
        if_not_exists=True,
    )
