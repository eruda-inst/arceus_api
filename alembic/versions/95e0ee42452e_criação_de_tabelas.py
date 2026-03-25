"""criação de tabelas

Revision ID: 95e0ee42452e
Revises:
Create Date: 2026-03-25 11:03:03.012825

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "95e0ee42452e"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ip", sa.String(), nullable=False),
        sa.Column("http_method", sa.String(), nullable=False),
        sa.Column("endpoint", sa.String(), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("hora", sa.Time(), nullable=False),
        sa.Column("duracao", sa.Numeric(10, 2), nullable=False),
        sa.Column("protocolo", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_logs_id"), "logs", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_logs_id", table_name="logs")
    op.drop_table("logs")
