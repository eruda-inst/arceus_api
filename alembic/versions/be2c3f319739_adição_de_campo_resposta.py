"""adição de campo "resposta"

Revision ID: be2c3f319739
Revises: ead6bce06197
Create Date: 2026-06-01 16:08:36.483180

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "be2c3f319739"
down_revision: Union[str, Sequence[str], None] = "ead6bce06197"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("logs", sa.Column("resposta", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("logs", "resposta")
