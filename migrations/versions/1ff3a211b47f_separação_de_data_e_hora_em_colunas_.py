from typing import Sequence, Union
from datetime import datetime as dt

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = "1ff3a211b47f"
down_revision: Union[str, Sequence[str], None] = "bbb5f03fe570"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    insp = sa.inspect(bind)
    columns = {c["name"] for c in insp.get_columns("logs")}

    # 1. Adicionar novas colunas, se ainda não existirem
    if "data" not in columns:
        op.add_column("logs", sa.Column("data", sa.Date(), nullable=True))

    if "hora" not in columns:
        op.add_column("logs", sa.Column("hora", sa.Time(), nullable=True))

    # Atualizar o inspetor depois das ADD COLUMN
    insp = sa.inspect(bind)
    columns = {c["name"] for c in insp.get_columns("logs")}

    # 2. Se ainda existir a coluna datetime, migrar os dados
    if "datetime" in columns:
        results = bind.execute(sa.text("SELECT id, datetime FROM logs"))

        for row in results:
            if row.datetime is not None:
                bind.execute(
                    sa.text(
                        "UPDATE logs "
                        "SET data = :data, hora = :hora "
                        "WHERE id = :id"
                    ),
                    {
                        "data": row.datetime.date(),
                        "hora": row.datetime.time(),
                        "id": row.id,
                    },
                )

        # 3. Só faz NOT NULL se as colunas existirem mesmo
        op.alter_column("logs", "data", existing_type=sa.Date(), nullable=False)
        op.alter_column("logs", "hora", existing_type=sa.Time(), nullable=False)

        # 4. Remover a coluna datetime original
        op.drop_column("logs", "datetime")


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    insp = sa.inspect(bind)
    columns = {c["name"] for c in insp.get_columns("logs")}

    # 1. Garantir que a coluna datetime exista
    if "datetime" not in columns:
        op.add_column(
            "logs",
            sa.Column("datetime", postgresql.TIMESTAMP(), nullable=True),
        )

    insp = sa.inspect(bind)
    columns = {c["name"] for c in insp.get_columns("logs")}

    # 2. Se tiver data e hora, recombina em datetime
    if "data" in columns and "hora" in columns:
        results = bind.execute(sa.text("SELECT id, data, hora FROM logs"))

        for row in results:
            if row.data and row.hora:
                datetime_combined = dt.combine(row.data, row.hora)
                bind.execute(
                    sa.text(
                        "UPDATE logs " "SET datetime = :datetime " "WHERE id = :id"
                    ),
                    {
                        "datetime": datetime_combined,
                        "id": row.id,
                    },
                )

        # 3. Tornar datetime NOT NULL
        op.alter_column(
            "logs",
            "datetime",
            existing_type=postgresql.TIMESTAMP(),
            nullable=False,
        )

    # 4. Remover as colunas data e hora, se existirem
    if "hora" in columns:
        op.drop_column("logs", "hora")
    if "data" in columns:
        op.drop_column("logs", "data")
