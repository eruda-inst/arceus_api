from collections.abc import Sequence

from fastapi import HTTPException, status
from pydantic import NonNegativeInt, PositiveInt
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .. import models


class GroupCrud:
    @staticmethod
    async def get_by(
        db: AsyncSession,
        id: PositiveInt | None = None,
        nome: str | None = None,
        id_usuario: PositiveInt | None = None,
        load_permissoes: bool = False,
    ) -> models.GroupModel:
        # If id is provided, filter by it
        if id is not None:
            stmt = select(models.GroupModel).where(models.GroupModel.id == id)
        # If nome is provided, filter by it
        elif nome is not None:
            stmt = select(models.GroupModel).where(models.GroupModel.nome == nome)
        # If id_usuario is provided, filter by it
        elif id_usuario is not None:
            stmt = (
                select(models.GroupModel)
                .join(
                    models.UserModel, models.UserModel.id_grupo == models.GroupModel.id
                )
                .where(models.UserModel.id == id_usuario)
            )
        # Raise a bad request if no param is provided
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Forneça id, nome ou id_usuario",
            )

        # If load_permissoes is True, load the group's perms
        if load_permissoes:
            stmt = stmt.options(selectinload(models.GroupModel.permissoes))

        group = (await db.execute(stmt)).scalar_one_or_none()

        # Raise a not found if no group is found
        if group is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Grupo inexistente"
            )

        return group

    @staticmethod
    async def get_all(
        db: AsyncSession,
    ) -> tuple[NonNegativeInt, Sequence[models.GroupModel]]:
        # Asc is default, but it's good to be explicit
        stmt = select(models.GroupModel).order_by(models.GroupModel.id.asc())
        groups = (await db.execute(stmt)).scalars().all()

        count_stmt = select(func.count(models.GroupModel.id))
        total_items = (await db.execute(count_stmt)).scalar()
        total_items = total_items if total_items is not None else 0

        return total_items, groups
