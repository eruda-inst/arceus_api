"""
CRUD operations for Permission (Perm) model.
"""

from collections.abc import Sequence

from fastapi import HTTPException, status
from pydantic import NonNegativeInt, PositiveInt
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from .. import models


class PermCrud:
    """
    Provides static methods for permission-related database operations.
    """

    @staticmethod
    async def get_by(
        db: AsyncSession,
        id: PositiveInt | None = None,
        name: str | None = None,
        code: str | None = None,
        load_groups: bool = False,
    ):
        """
        Retrieve a single permission by id, name, or code.

        Args:
            db: Async database session.
            id: Permission ID.
            name: Permission name.
            code: Permission code.
            load_groups: If True, eagerly load the permission's groups.

        Returns:
            The found PermModel instance.

        Raises:
            HTTPException: 400 if no search parameter is provided.
            HTTPException: 404 if the permission does not exist.
        """
        if id is not None:
            stmt = select(models.PermModel).where(models.PermModel.id == id)
        elif name is not None:
            stmt = select(models.PermModel).where(models.PermModel.nome == name)
        elif code is not None:
            stmt = select(models.PermModel).where(models.PermModel.codigo == code)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Forneça id, nome ou codigo",
            )

        if load_groups:
            stmt = stmt.options(selectinload(models.PermModel.grupos))

        perm = (await db.execute(stmt)).scalar_one_or_none()

        if perm is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Permissão inexistente"
            )

        return perm

    @staticmethod
    async def get_all_by(
        db: AsyncSession,
        group_id: PositiveInt | None = None,
        user_id: PositiveInt | None = None,
    ) -> tuple[NonNegativeInt, Sequence[models.PermModel]]:
        """
        Retrieve permissions filtered by group or user.

        Args:
            db: Async database session.
            group_id: Filter permissions belonging to this group ID.
            user_id: Filter permissions belonging to this user ID.

        Returns:
            A tuple with total count and sequence of PermModel instances.

        Raises:
            HTTPException: 400 if neither group_id nor user_id is provided.
        """
        stmt = select(models.PermModel)
        count_stmt = select(func.count(models.PermModel.id))

        if group_id is not None:
            stmt = stmt.join(models.PermModel.grupos).where(
                models.GroupModel.id == group_id
            )
            count_stmt = count_stmt.join(models.PermModel.grupos).where(
                models.GroupModel.id == group_id
            )
        elif user_id is not None:
            stmt = (
                stmt.join(models.PermModel.grupos)
                .join(models.GroupModel.usuarios)
                .where(models.UserModel.id == user_id)
            )
            count_stmt = (
                count_stmt.join(models.PermModel.grupos)
                .join(models.GroupModel.usuarios)
                .where(models.UserModel.id == user_id)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Forneça id_grupo ou id_usuario",
            )

        stmt = stmt.order_by(models.PermModel.id.asc())

        users = (await db.execute(stmt)).scalars().all()

        total_items = (await db.execute(count_stmt)).scalar()
        total_items = total_items if total_items is not None else 0

        return total_items, users
