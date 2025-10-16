"""Description of your changes

Revision ID: 6f1e1a91d9ac
Revises: adf854c026a5
Create Date: 2025-10-16 14:11:07.724876

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f1e1a91d9ac'
down_revision: Union[str, Sequence[str], None] = 'adf854c026a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
