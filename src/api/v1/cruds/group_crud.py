"""
CRUD operations for Group model.
"""

from collections.abc import Sequence

from fastapi import HTTPException, status
from pydantic import NonNegativeInt, PositiveInt
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .. import models


class GroupCrud:
    """
    Provides static methods for group-related database operations.
    """

    @staticmethod
    async def get_by(
        db: AsyncSession,
        id: PositiveInt | None = None,
        name: str | None = None,
        user_id: PositiveInt | None = None,
        load_perms: bool = False,
    ) -> models.GroupModel:
        """
        Retrieve a single group by id, name, or user id.

        Args:
            db: Async database session.
            id: Group ID to search for.
            name: Group name to search for.
            user_id: User ID to find the associated group.
            load_perms: If True, eagerly load the group's permissions.

        Returns:
            The found GroupModel instance.

        Raises:
            HTTPException: 400 if no search parameter is provided.
            HTTPException: 404 if the group does not exist.
        """
        if id is not None:
            stmt = select(models.GroupModel).where(models.GroupModel.id == id)
        elif name is not None:
            stmt = select(models.GroupModel).where(models.GroupModel.nome == name)
        elif user_id is not None:
            stmt = (
                select(models.GroupModel)
                .join(
                    models.UserModel, models.UserModel.id_grupo == models.GroupModel.id
                )
                .where(models.UserModel.id == user_id)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Forneça id, nome ou id_usuario",
            )

        if load_perms:
            stmt = stmt.options(selectinload(models.GroupModel.permissoes))

        group = (await db.execute(stmt)).scalar_one_or_none()

        if group is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Grupo inexistente"
            )

        return group

    @staticmethod
    async def get_all(
        db: AsyncSession,
    ) -> tuple[NonNegativeInt, Sequence[models.GroupModel]]:
        """
        Retrieve all groups ordered by ID.

        Args:
            db: Async database session.

        Returns:
            A tuple containing the total count of groups and a sequence of GroupModel instances.
        """
        stmt = select(models.GroupModel).order_by(models.GroupModel.id.asc())
        groups = (await db.execute(stmt)).scalars().all()

        count_stmt = select(func.count(models.GroupModel.id))
        total_items = (await db.execute(count_stmt)).scalar()
        total_items = total_items if total_items is not None else 0

        return total_items, groups
