"""adição de campo "resposta"

Revision ID: be2c3f319739
Revises: ead6bce06197
Create Date: 2026-06-01 16:08:36.483180

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "be2c3f319739"
down_revision: str | Sequence[str] | None = "ead6bce06197"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "logs", sa.Column("resposta", sa.String(), nullable=True), if_not_exists=True
    )


def downgrade() -> None:
    op.drop_column("logs", "resposta", if_exists=True)
