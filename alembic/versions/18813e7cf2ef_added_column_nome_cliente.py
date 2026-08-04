"""added column nome_cliente

Revision ID: 18813e7cf2ef
Revises: 6b71b98c1b99
Create Date: 2026-07-20 17:18:04.139954

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "18813e7cf2ef"
down_revision: str | Sequence[str] | None = "6b71b98c1b99"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        table_name="logs",
        column=sa.Column("nome_cliente", sa.String(), nullable=True),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_column(table_name="logs", column_name="nome_cliente", if_exists=True)
