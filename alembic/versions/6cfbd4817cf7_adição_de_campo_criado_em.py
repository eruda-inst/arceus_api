"""adição de campo criado_em

Revision ID: 6cfbd4817cf7
Revises: 522c4ff10e27
Create Date: 2026-07-17 09:07:24.215309

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6cfbd4817cf7"
down_revision: str | Sequence[str] | None = "522c4ff10e27"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "logs",
        sa.Column(
            "criado_em",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.timezone("America/Bahia", sa.func.now()),
            nullable=False,
        ),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_column("logs", "criado_em", if_exists=True)
