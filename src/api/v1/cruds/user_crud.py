from collections.abc import Sequence

from argon2 import PasswordHasher
from fastapi import HTTPException, status
from pydantic import EmailStr, NonNegativeInt, PositiveInt
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from .. import models, schemas, websockets

ph = PasswordHasher()


class UserCrud:
    @staticmethod
    async def create(db: AsyncSession, data: schemas.UserInSchema) -> models.UserModel:
        # Update user password to a hash password
        user_data = data.model_dump()
        user_data["senha"] = data.get_hash()
        new_user = models.UserModel(**user_data)

        # Add new user to database
        db.add(new_user)

        # Try to commit it
        try:
            await db.commit()
        except IntegrityError:
            # If user already exists, the operation is reverted
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Usuário já existe"
            )

        await db.refresh(new_user)
        await websockets.user_manager.broadcast()

        return new_user

    @staticmethod
    async def get_by(
        db: AsyncSession, id: PositiveInt | None = None, email: EmailStr | None = None
    ) -> models.UserModel | None:
        # If id is provided, it's used in the query
        if id is not None:
            stmt = select(models.UserModel).where(models.UserModel.id == id)
        # If email is provided, it's used in the query
        elif email is not None:
            stmt = select(models.UserModel).where(models.UserModel.email == email)
        # If neither is provided, it's raised bad request
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Forneça id ou email"
            )

        stmt = stmt.options(selectinload(models.UserModel.grupo))

        user = (await db.execute(stmt)).scalar_one_or_none()

        # Raise a not found if no user is found
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
        stmt = select(models.UserModel)
        count_stmt = select(func.count(models.UserModel.id))

        # Filter and count by name
        if name is not None:
            stmt = stmt.where(models.UserModel.nome.ilike(f"%{name}%"))
            count_stmt = count_stmt.where(models.UserModel.nome.ilike(f"%{name}%"))
        # Filter and count by e-mail
        if email is not None:
            stmt = stmt.where(models.UserModel.email.ilike(f"%{email}%"))
            count_stmt = count_stmt.where(models.UserModel.email.ilike(f"%{email}%"))
        # Filter and count by status
        if active is not None:
            stmt = stmt.where(models.UserModel.ativo == active)
            count_stmt = count_stmt.where(models.UserModel.ativo == active)
        # Filter and count by id
        if group_id is not None:
            stmt = stmt.where(models.UserModel.id_grupo == group_id)
            count_stmt = count_stmt.where(models.UserModel.id_grupo == group_id)
        # Filter and count by group name
        if group_name is not None:
            stmt = stmt.join(models.UserModel.grupo).where(
                models.GroupModel.nome.ilike(f"%{group_name}%")
            )
            count_stmt = count_stmt.join(models.UserModel.grupo).where(
                models.GroupModel.nome.ilike(f"%{group_name}%")
            )

        stmt = stmt.options(selectinload(models.UserModel.grupo))

        # Total items for meta info
        total_items = (await db.execute(count_stmt)).scalar()
        total_items = total_items if total_items is not None else 0

        # Ordering
        # Ordering should be before pagination
        # Asc is default, but it's good to be explicit
        stmt = stmt.order_by(models.UserModel.id.asc())

        # Pagination
        offset = (page - 1) * items_per_page
        stmt = stmt.offset(offset).limit(items_per_page)

        # Users
        users = (await db.execute(stmt)).scalars().all()
        return total_items, users

    @staticmethod
    async def del_by_id(db: AsyncSession, id: PositiveInt) -> None:
        # Retrieve the current user by id
        stmt = select(models.UserModel).where(models.UserModel.id == id)
        user = (await db.execute(stmt)).scalar_one_or_none()

        # Raise not found if no user exists with the given id
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário inexistente"
            )

        # Delete the user instance (marked for deletion, not yet committed)
        await db.delete(user)

        # Attempt to commit the deletion
        try:
            await db.commit()
        except SQLAlchemyError:
            # Rollback to leave the session in a clean state
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

        await websockets.user_manager.broadcast()

    @staticmethod
    async def toggle_status_by_id(
        db: AsyncSession, id: PositiveInt
    ) -> models.UserModel | None:
        # Retrieve the current user by id
        stmt = select(models.UserModel).where(models.UserModel.id == id)
        user = (await db.execute(stmt)).scalar_one_or_none()

        # Raise not found if no user exists with the given id
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário inexistente"
            )

        user.ativo = not bool(user.ativo)  # type: ignore

        # Attempt to commit the change
        try:
            await db.commit()
        except SQLAlchemyError:
            # Rollback to leave the session in a clean state
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

        # Refresh the instance to load any database-generated defaults or updates
        await db.refresh(user)
        await websockets.user_manager.broadcast()

        return user

    @staticmethod
    async def update_pwd_by_id(
        db: AsyncSession, id: PositiveInt, new_pwd: str
    ) -> models.UserModel:
        # Retrieve the current user by id
        stmt = select(models.UserModel).where(models.UserModel.id == id)
        user = (await db.execute(stmt)).scalar_one_or_none()

        # Raise not found if no user exists with the given id
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário inexistente"
            )

        user.senha = ph.hash(password=new_pwd)  # type: ignore

        # Attempt to commit the change
        try:
            await db.commit()
        except SQLAlchemyError:
            # Rollback to leave the session in a clean state
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

        # Refresh the instance to load any database-generated defaults or updates
        await db.refresh(user)

        return user
