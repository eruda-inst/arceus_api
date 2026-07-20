"""column resposta is not nullable

Revision ID: ee16933c1ce4
Revises: f51141987f8d
Create Date: 2026-07-20 09:20:08.071022

"""

from alembic import op
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "ee16933c1ce4"
down_revision: Union[str, Sequence[str], None] = "f51141987f8d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(table_name="logs", column_name="resposta", nullable=False)


def downgrade() -> None:
    op.alter_column(table_name="logs", column_name="resposta", nullable=True)
