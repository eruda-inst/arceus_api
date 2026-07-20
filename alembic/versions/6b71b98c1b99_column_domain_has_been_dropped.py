"""column domain has been dropped

Revision ID: 6b71b98c1b99
Revises: ee16933c1ce4
Create Date: 2026-07-20 15:48:22.080553

"""

from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "6b71b98c1b99"
down_revision: Union[str, Sequence[str], None] = "ee16933c1ce4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column(table_name="logs", column_name="dominio", if_exists=True)


def downgrade() -> None:
    op.add_column(
        table_name="logs",
        column=sa.Column("dominio", sa.String(), nullable=False),
        if_not_exists=True,
    )
