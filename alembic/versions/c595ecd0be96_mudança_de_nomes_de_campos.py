"""mudança de nomes de campos

Revision ID: c595ecd0be96
Revises: 95e0ee42452e
Create Date: 2026-03-27 17:05:28.863601

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c595ecd0be96"
down_revision: str | Sequence[str] | None = "95e0ee42452e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        table_name="logs", column_name="http_method", new_column_name="metodo"
    )
    op.alter_column(
        table_name="logs", column_name="status_code", new_column_name="codigo"
    )


def downgrade() -> None:
    op.alter_column(
        table_name="logs", column_name="metodo", new_column_name="http_method"
    )
    op.alter_column(
        table_name="logs", column_name="codigo", new_column_name="status_code"
    )
