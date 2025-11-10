"""adicionada nova coluna na tabela, coluna 'protocolo'

Revision ID: e8dcca57086b
Revises: 1ff3a211b47f
Create Date: 2025-11-10 20:07:07.188661
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "e8dcca57086b"
down_revision: Union[str, Sequence[str], None] = "1ff3a211b47f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: adiciona coluna 'protocolo' em logs."""
    # 1. Adiciona a coluna com um default vazio pra não quebrar linha antiga
    op.add_column(
        "logs",
        sa.Column(
            "protocolo",
            sa.String(),
            nullable=False,
            server_default="",
        ),
    )
    # 2. (Opcional) remove o default no schema do banco, se não quiser manter
    op.alter_column("logs", "protocolo", server_default=None)


def downgrade() -> None:
    """Downgrade schema: remove coluna 'protocolo' de logs."""
    op.drop_column("logs", "protocolo")
