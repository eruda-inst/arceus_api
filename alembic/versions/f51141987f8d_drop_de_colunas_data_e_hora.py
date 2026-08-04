"""drop de colunas data e hora

Revision ID: f51141987f8d
Revises: f0a4c6954f13
Create Date: 2026-07-17 14:02:49.294855

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f51141987f8d"
down_revision: str | Sequence[str] | None = "f0a4c6954f13"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_column(table_name="logs", column_name="data", if_exists=True)
    op.drop_column(table_name="logs", column_name="hora", if_exists=True)


def downgrade() -> None:
    op.add_column(
        table_name="logs",
        column=sa.Column("data", sa.String(), nullable=False),
        if_not_exists=True,
    )
    op.add_column(
        table_name="logs",
        column=sa.Column("hora", sa.String(), nullable=False),
        if_not_exists=True,
    )
