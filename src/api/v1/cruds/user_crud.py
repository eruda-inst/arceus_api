"""
CRUD operations for User model.
"""

from collections.abc import Sequence

from argon2 import PasswordHasher
from fastapi import HTTPException, status
from pydantic import EmailStr, NonNegativeInt, PositiveInt
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from .. import models, schemas, ws

ph = PasswordHasher()


class UserCrud:
    """
    Provides static methods for user-related database operations.
    """

    @staticmethod
    async def create(db: AsyncSession, data: schemas.UserInSchema) -> models.UserModel:
        """
        Create a new user.

        Args:
            db: Async database session.
            data: User input schema containing user details.

        Returns:
            The newly created UserModel instance.

        Raises:
            HTTPException: 409 if the user already exists (integrity error).
        """
        user_data = data.model_dump()
        user_data["senha"] = data.get_hash()
        new_user = models.UserModel(**user_data)

        db.add(new_user)

        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Usuário já existe"
            )

        await db.refresh(new_user)
        await ws.user_manager.broadcast()

        return new_user

    @staticmethod
    async def get_by(
        db: AsyncSession, id: PositiveInt | None = None, email: EmailStr | None = None
    ) -> models.UserModel | None:
        """
        Retrieve a user by ID or email.

        Args:
            db: Async database session.
            id: User ID.
            email: User email.

        Returns:
            The found UserModel instance, with group eagerly loaded.

        Raises:
            HTTPException: 400 if neither id nor email is provided.
            HTTPException: 404 if the user does not exist.
        """
        if id is not None:
            stmt = select(models.UserModel).where(models.UserModel.id == id)
        elif email is not None:
            stmt = select(models.UserModel).where(models.UserModel.email == email)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Forneça id ou email"
            )

        stmt = stmt.options(selectinload(models.UserModel.grupo))

        user = (await db.execute(stmt)).scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário inexistente"
            )

        return user

    @staticmethod
    async def get_all_by(
        db: AsyncSession,
        page: PositiveInt,
        items_per_page: PositiveInt,
        name: str | None = None,
        email: str | None = None,
        active: bool | None = None,
        group_id: PositiveInt | None = None,
        group_name: str | None = None,
    ) -> tuple[NonNegativeInt, Sequence[models.UserModel]]:
        """
        Retrieve users with optional filters and pagination.

        Args:
            db: Async database session.
            page: Page number (1-based).
            items_per_page: Number of items per page.
            name: Filter by user name (partial match).
            email: Filter by email (partial match).
            active: Filter by active status.
            group_id: Filter by group ID.
            group_name: Filter by group name (partial match).

        Returns:
            A tuple with total number of matching users and the paginated sequence.
        """
        stmt = select(models.UserModel)
        count_stmt = select(func.count(models.UserModel.id))

        if name is not None:
            stmt = stmt.where(models.UserModel.nome.ilike(f"%{name}%"))
            count_stmt = count_stmt.where(models.UserModel.nome.ilike(f"%{name}%"))
        if email is not None:
            stmt = stmt.where(models.UserModel.email.ilike(f"%{email}%"))
            count_stmt = count_stmt.where(models.UserModel.email.ilike(f"%{email}%"))
        if active is not None:
            stmt = stmt.where(models.UserModel.ativo == active)
            count_stmt = count_stmt.where(models.UserModel.ativo == active)
        if group_id is not None:
            stmt = stmt.where(models.UserModel.id_grupo == group_id)
            count_stmt = count_stmt.where(models.UserModel.id_grupo == group_id)
        if group_name is not None:
            stmt = stmt.join(models.UserModel.grupo).where(
                models.GroupModel.nome.ilike(f"%{group_name}%")
            )
            count_stmt = count_stmt.join(models.UserModel.grupo).where(
                models.GroupModel.nome.ilike(f"%{group_name}%")
            )

        stmt = stmt.options(selectinload(models.UserModel.grupo))

        total_items = (await db.execute(count_stmt)).scalar()
        total_items = total_items if total_items is not None else 0

        stmt = stmt.order_by(models.UserModel.id.asc())

        offset = (page - 1) * items_per_page
        stmt = stmt.offset(offset).limit(items_per_page)

        users = (await db.execute(stmt)).scalars().all()
        return total_items, users

    @staticmethod
    async def del_by_id(db: AsyncSession, id: PositiveInt) -> None:
        """
        Delete a user by ID.

        Args:
            db: Async database session.
            id: User ID.

        Raises:
            HTTPException: 404 if the user does not exist.
            HTTPException: 500 if a database error occurs.
        """
        stmt = select(models.UserModel).where(models.UserModel.id == id)
        user = (await db.execute(stmt)).scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário inexistente"
            )

        await db.delete(user)

        try:
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

        await ws.user_manager.broadcast()

    @staticmethod
    async def toggle_status_by_id(
        db: AsyncSession, id: PositiveInt
    ) -> models.UserModel | None:
        """
        Toggle the active status of a user by ID.

        Args:
            db: Async database session.
            id: User ID.

        Returns:
            The updated UserModel instance.

        Raises:
            HTTPException: 404 if the user does not exist.
            HTTPException: 500 if a database error occurs.
        """
        stmt = (
            select(models.UserModel)
            .where(models.UserModel.id == id)
            .options(selectinload(models.UserModel.grupo))
        )
        user = (await db.execute(stmt)).scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário inexistente"
            )

        user.ativo = not bool(user.ativo)  # type: ignore

        try:
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

        await db.refresh(user)
        await ws.user_manager.broadcast()

        return user

    @staticmethod
    async def update_pass_by_id(
        db: AsyncSession, id: PositiveInt, new_pass: str
    ) -> models.UserModel:
        """
        Update a user's password by ID.

        Args:
            db: Async database session.
            id: User ID.
            new_pass: New plaintext password.

        Returns:
            The updated UserModel instance.

        Raises:
            HTTPException: 404 if the user does not exist.
            HTTPException: 500 if a database error occurs.
        """
        stmt = (
            select(models.UserModel)
            .where(models.UserModel.id == id)
            .options(selectinload(models.UserModel.grupo))
        )
        user = (await db.execute(stmt)).scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário inexistente"
            )

        user.senha = ph.hash(password=new_pass)  # type: ignore

        try:
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

        await db.refresh(user)

        return user
