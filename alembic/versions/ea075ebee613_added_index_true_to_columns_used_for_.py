"""added index=true to columns used for filtering

Revision ID: ea075ebee613
Revises: 18813e7cf2ef
Create Date: 2026-07-27 09:58:08.381667

"""

from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "ea075ebee613"
down_revision: Union[str, Sequence[str], None] = "18813e7cf2ef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(table_name="logs", column_name="id", unique=True, nullable=False)
    op.alter_column(
        table_name="logs",
        column_name="metodo",
        unique=False,
        nullable=False,
        index=True,
    )
    op.alter_column(
        table_name="logs",
        column_name="endpoint",
        unique=False,
        nullable=False,
        index=True,
    )
    op.alter_column(
        table_name="logs",
        column_name="codigo",
        unique=False,
        nullable=False,
        index=True,
    )
    op.alter_column(
        table_name="logs",
        column_name="duracao",
        type_=sa.Numeric(10, 3),
        unique=False,
        nullable=False,
        index=False,
    )
    op.alter_column(
        table_name="logs",
        column_name="protocolo",
        unique=False,
        nullable=True,
        index=True,
    )
    op.alter_column(
        table_name="logs",
        column_name="payload",
        unique=False,
        nullable=True,
        index=False,
    )
    op.alter_column(
        table_name="logs",
        column_name="resposta",
        unique=False,
        nullable=True,
        index=False,
    )
    op.alter_column(
        table_name="logs", column_name="url", unique=False, nullable=False, index=False
    )
    op.alter_column(
        table_name="logs", column_name="setor", unique=False, nullable=True, index=True
    )
    op.alter_column(
        table_name="logs",
        column_name="nome_cliente",
        unique=False,
        nullable=True,
        index=True,
    )


def downgrade() -> None:
    op.alter_column(table_name="logs", column_name="id", unique=None, nullable=None)
    op.alter_column(
        table_name="logs", column_name="metodo", unique=None, nullable=None, index=None
    )
    op.alter_column(
        table_name="logs",
        column_name="endpoint",
        unique=None,
        nullable=None,
        index=None,
    )
    op.alter_column(
        table_name="logs", column_name="codigo", unique=None, nullable=None, index=None
    )
    op.alter_column(
        table_name="logs",
        column_name="duracao",
        type_=sa.Numeric(10, 2),
        unique=None,
        nullable=None,
        index=None,
    )
    op.alter_column(
        table_name="logs",
        column_name="protocolo",
        unique=None,
        nullable=True,
        index=None,
    )
    op.alter_column(
        table_name="logs", column_name="payload", unique=None, nullable=None, index=None
    )
    op.alter_column(
        table_name="logs",
        column_name="resposta",
        unique=None,
        nullable=None,
        index=None,
    )
    op.alter_column(
        table_name="logs", column_name="url", unique=None, nullable=None, index=None
    )
    op.alter_column(
        table_name="logs", column_name="setor", unique=None, nullable=None, index=None
    )
    op.alter_column(
        table_name="logs",
        column_name="nome_cliente",
        unique=None,
        nullable=None,
        index=None,
    )
