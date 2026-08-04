"""inserting perms and groups

Revision ID: a3bececb0996
Revises: 7a336d048eac
Create Date: 2026-08-03 15:44:10.068158

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op
from src.api.v1.utils.enums.group_enum import GroupNames
from src.api.v1.utils.enums.perm_enum import PermCodes, PermNames

# revision identifiers, used by Alembic.
revision: str = "a3bececb0996"
down_revision: str | Sequence[str] | None = "7a336d048eac"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


ADMIN_GROUP_NAME = GroupNames.ADMIN.value
ANALIST_GROUP_NAME = GroupNames.ANALIST.value

READ_METRIC_CODE = PermCodes.READ_METRIC.value
READ_METRIC_NAME = PermNames.READ_METRIC.value

READ_LOG_CODE = PermCodes.READ_LOG.value
READ_LOG_NAME = PermNames.READ_LOG.value

CREATE_USER_CODE = PermCodes.CREATE_USER.value
CREATE_USER_NAME = PermNames.CREATE_USER.value

READ_USER_CODE = PermCodes.READ_USER.value
READ_USER_NAME = PermNames.READ_USER.value

UPDATE_USER_CODE = PermCodes.UPDATE_USER.value
UPDATE_USER_NAME = PermNames.UPDATE_USER.value

DEL_USER_CODE = PermCodes.DEL_USER.value
DEL_USER_NAME = PermNames.DEL_USER.value


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. Grupo "Administrador"
    # ------------------------------------------------------------------
    op.execute(
        sa.text("""
            INSERT INTO grupos (nome)
            SELECT :nome
            WHERE NOT EXISTS (
                SELECT 1 FROM grupos WHERE nome = :nome
            );
        """).bindparams(
            nome=ADMIN_GROUP_NAME,
        ),
    )
    # ------------------------------------------------------------------
    # 2. Grupo "Analista"
    # ------------------------------------------------------------------
    op.execute(
        sa.text("""
                INSERT INTO grupos (nome)
                SELECT :nome
                WHERE NOT EXISTS (
                    SELECT 1 FROM grupos WHERE nome = :nome
                );
        """).bindparams(
            nome=ANALIST_GROUP_NAME,
        ),
    )
    # ------------------------------------------------------------------
    # 3. Permissões de métricas
    # Operações: ver
    # ------------------------------------------------------------------
    op.execute(
        sa.text("""
            INSERT INTO permissoes (nome, codigo)
            SELECT :read_metric_name, :read_metric_code
            WHERE NOT EXISTS (
                SELECT 1 FROM permissoes WHERE codigo = :read_metric_code
            );
        """).bindparams(
            read_metric_name=READ_METRIC_NAME,
            read_metric_code=READ_METRIC_CODE,
        )
    )
    # ------------------------------------------------------------------
    # 4. Permissões de logs
    # Operações: ver
    # ------------------------------------------------------------------
    op.execute(
        sa.text("""
                INSERT INTO permissoes (nome, codigo)
                SELECT :read_logs_name, :read_logs_code
                WHERE NOT EXISTS (
                    SELECT 1 FROM permissoes WHERE codigo = :read_logs_code
                );
            """).bindparams(
            read_logs_name=READ_LOG_NAME,
            read_logs_code=READ_LOG_CODE,
        )
    )
    # ------------------------------------------------------------------
    # 5. Permissões de usuários
    # Operações: criar, ver, alterar, remover
    # ------------------------------------------------------------------
    op.execute(
        sa.text("""
            INSERT INTO permissoes (nome, codigo)
            SELECT :create_users_name, :create_users_code
            WHERE NOT EXISTS (
                SELECT 1 FROM permissoes WHERE codigo = :create_users_code
            );
        """).bindparams(
            create_users_name=CREATE_USER_NAME,
            create_users_code=CREATE_USER_CODE,
        )
    )
    op.execute(
        sa.text("""
            INSERT INTO permissoes (nome, codigo)
            SELECT :read_users_name, :read_users_code
            WHERE NOT EXISTS (
                SELECT 1 FROM permissoes WHERE codigo = :read_users_code
            );
        """).bindparams(
            read_users_name=READ_USER_NAME,
            read_users_code=READ_USER_CODE,
        )
    )
    op.execute(
        sa.text("""
            INSERT INTO permissoes (nome, codigo)
            SELECT :update_users_name, :update_users_code
            WHERE NOT EXISTS (
                SELECT 1 FROM permissoes WHERE codigo = :update_users_code
            );
        """).bindparams(
            update_users_name=UPDATE_USER_NAME,
            update_users_code=UPDATE_USER_CODE,
        )
    )
    op.execute(
        sa.text("""
            INSERT INTO permissoes (nome, codigo)
            SELECT :del_users_name, :del_users_code
            WHERE NOT EXISTS (
                SELECT 1 FROM permissoes WHERE codigo = :del_users_code
            );
        """).bindparams(
            del_users_name=DEL_USER_NAME,
            del_users_code=DEL_USER_CODE,
        )
    )


def downgrade() -> None:
    # ------------------------------------------------------------------
    # 1. Removendo grupos "Administrador", "Analista"
    # ------------------------------------------------------------------
    op.execute(
        sa.text("""
            DELETE FROM grupos WHERE nome in (
                :admin_name,
                :analist_name
            );
        """).bindparams(
            admin_name=ADMIN_GROUP_NAME,
            analist_name=ANALIST_GROUP_NAME,
        )
    )
    # ------------------------------------------------------------------
    # 2. Removendo permissões para métricas, logs, usuários
    # ------------------------------------------------------------------
    op.execute(
        sa.text("""
            DELETE FROM permissoes WHERE codigo IN (
                :read_metric_code,
                :read_logs_code,
                :create_users_code,
                :read_users_code,
                :update_users_code,
                :del_users_code
            );
        """).bindparams(
            read_metric_code=READ_METRIC_CODE,
            read_logs_code=READ_LOG_CODE,
            create_users_code=CREATE_USER_CODE,
            read_users_code=READ_USER_CODE,
            update_users_code=UPDATE_USER_CODE,
            del_users_code=DEL_USER_CODE,
        )
    )
