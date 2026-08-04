from collections.abc import Sequence

from fastapi import HTTPException, status
from pydantic import NonNegativeInt, PositiveInt
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from .. import models


class PermCrud:
    @staticmethod
    async def get_by(
        db: AsyncSession,
        id: PositiveInt | None = None,
        nome: str | None = None,
        codigo: str | None = None,
        load_grupos: bool = False,
    ):
        # If id is provided, filter by it
        if id is not None:
            stmt = select(models.Perm).where(models.Perm.id == id)
        # If nome is provided, filter by it
        elif nome is not None:
            stmt = select(models.Perm).where(models.Perm.nome == nome)
        # If codigo is provided, filter by it
        elif codigo is not None:
            stmt = select(models.Perm).where(models.Perm.codigo == codigo)
        # Raise bad request if no param is provided
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Forneça id, nome ou codigo",
            )

        # If load_grupos is True, the perm's groups are loaded
        if load_grupos:
            stmt = stmt.options(selectinload(models.Perm.grupos))

        perm = (await db.execute(stmt)).scalar_one_or_none()

        # Raise not found if no perm is found
        if perm is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Permissão inexistente"
            )

        return perm

    @staticmethod
    async def get_all_by(
        db: AsyncSession,
        id_grupo: PositiveInt | None = None,
        id_usuario: PositiveInt | None = None,
    ) -> tuple[NonNegativeInt, Sequence[models.Perm]]:
        stmt = select(models.Perm)
        count_stmt = select(func.count(models.Perm.id))

        # If id_grupo is provided, filter by it
        if id_grupo is not None:
            stmt = stmt.join(models.Perm.grupos).where(models.Group.id == id_grupo)
            count_stmt = count_stmt.join(models.Perm.grupos).where(
                models.Group.id == id_grupo
            )
        # If id_usuario is provided, filter by it
        elif id_usuario is not None:
            stmt = (
                stmt.join(models.Perm.grupos)
                .join(models.Group.usuarios)
                .where(models.User.id == id_usuario)
            )
            count_stmt = (
                count_stmt.join(models.Perm.grupos)
                .join(models.Group.usuarios)
                .where(models.User.id == id_usuario)
            )
        # Raise bad request if no param is provided
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Forneça id_grupo ou id_usuario",
            )

        # Ordering
        # Asc is default, but it's good to be explicit
        stmt = stmt.order_by(models.Perm.id.asc())

        users = (await db.execute(stmt)).scalars().all()

        # Count items
        total_items = (await db.execute(count_stmt)).scalar()
        total_items = total_items if total_items is not None else 0

        return total_items, users
