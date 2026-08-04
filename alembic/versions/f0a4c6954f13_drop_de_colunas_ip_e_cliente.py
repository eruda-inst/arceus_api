"""drop de colunas ip e cliente

Revision ID: f0a4c6954f13
Revises: 6cfbd4817cf7
Create Date: 2026-07-17 09:56:21.672977

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f0a4c6954f13"
down_revision: str | Sequence[str] | None = "6cfbd4817cf7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_column(table_name="logs", column_name="ip", if_exists=True)
    op.drop_column(table_name="logs", column_name="cliente", if_exists=True)


def downgrade() -> None:
    op.add_column(
        table_name="logs",
        column=sa.Column("ip", sa.String(), nullable=False),
        if_not_exists=True,
    )
    op.add_column(
        table_name="logs",
        column=sa.Column("cliente", sa.String(), nullable=False),
        if_not_exists=True,
    )
