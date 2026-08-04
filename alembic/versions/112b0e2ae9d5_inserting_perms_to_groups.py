"""inserting perms to groups

Revision ID: 112b0e2ae9d5
Revises: a3bececb0996
Create Date: 2026-08-03 15:45:14.346119

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op
from src.api.v1.utils.enums.group_enum import GroupNames
from src.api.v1.utils.enums.perm_enum import PermCodes

# revision identifiers, used by Alembic.
revision: str = "112b0e2ae9d5"
down_revision: str | Sequence[str] | None = "a3bececb0996"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


ADMIN_GROUP_NAME = GroupNames.ADMIN.value
ANALIST_GROUP_NAME = GroupNames.ANALIST.value

READ_METRIC_CODE = PermCodes.READ_METRIC.value
READ_LOG_CODE = PermCodes.READ_LOG.value

CREATE_USER_CODE = PermCodes.CREATE_USER.value
READ_USER_CODE = PermCodes.READ_USER.value
UPDATE_USER_CODE = PermCodes.UPDATE_USER.value
DEL_USER_CODE = PermCodes.DEL_USER.value


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. ANALISTA
    # Regra: Ver métricas + ver logs
    # ------------------------------------------------------------------
    op.execute(
        sa.text("""
            INSERT INTO grupos_permissoes (group_id, permission_id)
            SELECT g.id, p.id
            FROM grupos g, permissoes p
            WHERE g.nome = :group_name
            AND p.codigo = :perm_code
            AND NOT EXISTS (
                SELECT 1 FROM grupos_permissoes gp
                WHERE gp.group_id = g.id AND gp.permission_id = p.id
            )
        """).bindparams(
            group_name=ANALIST_GROUP_NAME,
            perm_code=READ_METRIC_CODE,
        )
    )
    op.execute(
        sa.text("""
            INSERT INTO grupos_permissoes (group_id, permission_id)
            SELECT g.id, p.id
            FROM grupos g, permissoes p
            WHERE g.nome = :group_name
            AND p.codigo = :perm_code
            AND NOT EXISTS (
                SELECT 1 FROM grupos_permissoes gp
                WHERE gp.group_id = g.id AND gp.permission_id = p.id
            )
        """).bindparams(
            group_name=ANALIST_GROUP_NAME,
            perm_code=READ_LOG_CODE,
        )
    )
    # ------------------------------------------------------------------
    # 2. ADMINISTRADOR
    # Regra: Ver métricas + Ver logs + CRUD usuários
    # ------------------------------------------------------------------
    op.execute(
        sa.text("""
            INSERT INTO grupos_permissoes (group_id, permission_id)
            SELECT g.id, p.id
            FROM grupos g, permissoes p
            WHERE g.nome = :group_name
            AND p.codigo IN (
                :read_metric_code,
                :read_logs_code,
                :create_users_code,
                :read_users_code,
                :update_users_code,
                :del_users_code
            )
            AND NOT EXISTS (
                SELECT 1 FROM grupos_permissoes gp
                WHERE gp.group_id = g.id AND gp.permission_id = p.id
            )
        """).bindparams(
            group_name=ADMIN_GROUP_NAME,
            read_metric_code=READ_METRIC_CODE,
            read_logs_code=READ_LOG_CODE,
            create_users_code=CREATE_USER_CODE,
            read_users_code=READ_USER_CODE,
            update_users_code=UPDATE_USER_CODE,
            del_users_code=DEL_USER_CODE,
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text("""
            DELETE FROM grupos_permissoes
            WHERE group_id IN (
                SELECT id FROM grupos WHERE nome in (
                    :analist_group_name,
                    :admin_group_name
                )
            );
        """).bindparams(
            analist_group_name=GroupNames.ANALIST,
            admin_group_name=GroupNames.ADMIN,
        )
    )
