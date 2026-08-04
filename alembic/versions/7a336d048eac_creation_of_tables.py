"""creation of tables

Revision ID: 7a336d048eac
Revises: ea075ebee613
Create Date: 2026-08-03 15:40:25.461523

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7a336d048eac"
down_revision: str | Sequence[str] | None = "ea075ebee613"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Grupos
    op.create_table(
        "grupos",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            primary_key=True,
            nullable=False,
            index=True,
            unique=True,
        ),
        sa.Column("nome", sa.String(), nullable=False, unique=True, index=False),
        sa.Column(
            "criado_em",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.timezone("America/Bahia", sa.func.now()),
            nullable=False,
            index=False,
            unique=False,
        ),
        if_not_exists=True,
    )
    # Permissões
    op.create_table(
        "permissoes",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            primary_key=True,
            nullable=False,
            index=True,
            unique=True,
        ),
        sa.Column("nome", sa.String(), nullable=False, unique=True, index=False),
        sa.Column("codigo", sa.String(), nullable=False, unique=True, index=False),
        sa.Column(
            "criado_em",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.timezone("America/Bahia", sa.func.now()),
            nullable=False,
            index=False,
            unique=False,
        ),
        if_not_exists=True,
    )
    # Grupos permissões
    op.create_table(
        "grupos_permissoes",
        sa.Column("group_id", sa.Integer(), nullable=True, index=False, unique=False),
        sa.Column(
            "permission_id", sa.Integer(), nullable=True, index=False, unique=False
        ),
        if_not_exists=True,
    )
    # Usuários
    op.create_table(
        "usuarios",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            primary_key=True,
            nullable=False,
            index=True,
            unique=True,
        ),
        sa.Column("nome", sa.String(), nullable=False, unique=True, index=False),
        sa.Column("email", sa.String(), nullable=False, unique=True, index=False),
        sa.Column("senha", sa.String(), nullable=False, unique=False, index=False),
        sa.Column(
            "ativo",
            sa.Boolean(),
            nullable=False,
            default=True,
            unique=False,
            index=False,
        ),
        sa.Column(
            "criado_em",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.timezone("America/Bahia", sa.func.now()),
            nullable=False,
            unique=False,
            index=False,
        ),
        sa.Column(
            "atualizado_em",
            sa.TIMESTAMP(timezone=True),
            onupdate=sa.func.timezone("America/Bahia", sa.func.now()),
            nullable=True,
            unique=False,
            index=False,
        ),
        sa.Column("id_grupo", sa.Integer(), nullable=False, index=False, unique=False),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.execute("DROP TABLE grupos_permissoes CASCADE;")
    op.execute("DROP TABLE permissoes CASCADE;")
    op.execute("DROP TABLE grupos CASCADE;")
    op.execute("DROP TABLE usuarios CASCADE;")
