"""campos payload e protocolo nullable

Revision ID: 522c4ff10e27
Revises: be2c3f319739
Create Date: 2026-07-16 15:49:23.075201

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "522c4ff10e27"
down_revision: str | Sequence[str] | None = "be2c3f319739"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(table_name="logs", column_name="payload", nullable=True)
    op.alter_column(table_name="logs", column_name="protocolo", nullable=True)


def downgrade() -> None:
    op.alter_column(table_name="logs", column_name="payload", nullable=False)
    op.alter_column(table_name="logs", column_name="protocolo", nullable=False)
