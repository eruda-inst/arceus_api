"""inserting default user

Revision ID: 562fd3594f91
Revises: 112b0e2ae9d5
Create Date: 2026-08-03 15:46:28.763514

"""

from collections.abc import Sequence

import sqlalchemy as sa
from argon2 import PasswordHasher

from alembic import op
from src.api.v1.config_core import settings
from src.api.v1.utils.enums.group_enum import GroupNames

# revision identifiers, used by Alembic.
revision: str = "562fd3594f91"
down_revision: str | Sequence[str] | None = "112b0e2ae9d5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


ph = PasswordHasher()

# Dados do usuário padrão
ADMIN_NOME = settings.dflt_user_name
ADMIN_EMAIL = settings.dflt_user_email
ADMIN_SENHA = settings.dflt_user_pass.get_secret_value()
GRUPO_ADMIN_NOME = GroupNames.ADMIN.value


def upgrade() -> None:
    # Gera o hash da senha
    hashed_password = ph.hash(password=ADMIN_SENHA)  # type: ignore

    # Insere o usuário apenas se não existir (baseado no email único)
    op.execute(
        sa.text("""
            INSERT INTO usuarios (nome, email, senha, ativo, id_grupo)
            SELECT :nome, :email, :senha, :ativo,
                (SELECT id FROM grupos WHERE nome = :grupo_nome)
            WHERE NOT EXISTS (
                SELECT 1 FROM usuarios WHERE email = :email
            );
        """).bindparams(
            nome=ADMIN_NOME,
            email=ADMIN_EMAIL,
            senha=hashed_password,
            ativo=True,
            grupo_nome=GRUPO_ADMIN_NOME,
        )
    )


def downgrade() -> None:
    # Remove o usuário administrador padrão
    op.execute(
        sa.text("""
            DELETE FROM usuarios
            WHERE email = :email;
        """).bindparams(
            email=ADMIN_EMAIL,
        ),
    )
