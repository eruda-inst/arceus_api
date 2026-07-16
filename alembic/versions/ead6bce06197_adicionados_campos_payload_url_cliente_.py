"""adicionados campos: payload, url, cliente, dominio, setor

Revision ID: ead6bce06197
Revises: c595ecd0be96
Create Date: 2026-04-13 09:57:42.705625

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "ead6bce06197"
down_revision: Union[str, Sequence[str], None] = "c595ecd0be96"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "logs", sa.Column("payload", sa.String(), nullable=False), if_not_exists=True
    )
    op.add_column(
        "logs", sa.Column("url", sa.String(), nullable=False), if_not_exists=True
    )
    op.add_column(
        "logs", sa.Column("cliente", sa.String(), nullable=False), if_not_exists=True
    )
    op.add_column(
        "logs", sa.Column("dominio", sa.String(), nullable=False), if_not_exists=True
    )
    op.add_column(
        "logs", sa.Column("setor", sa.String(), nullable=False), if_not_exists=True
    )


def downgrade() -> None:
    op.drop_column("logs", "setor", if_exists=True)
    op.drop_column("logs", "dominio", if_exists=True)
    op.drop_column("logs", "cliente", if_exists=True)
    op.drop_column("logs", "url", if_exists=True)
    op.drop_column("logs", "payload", if_exists=True)
