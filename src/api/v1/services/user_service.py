from pydantic import PositiveInt
from sqlalchemy.ext.asyncio import AsyncSession

from .. import cruds, schemas, services


class UsuarioService:
    @staticmethod
    async def create(
        db: AsyncSession, data: schemas.UserInSchema
    ) -> schemas.UserOutSchema:
        # Only users that exist in the external IXC system are allowed to be created locally.
        # If get_by_email() does not find the user, it raises a "not found" exception,
        # which prevents the local user from being created.
        _ = await services.IXCUserService.get_by_email(email=data.email)

        created_user = await cruds.UserCrud.create(db=db, data=data)

        return schemas.UserOutSchema.model_validate(created_user)

    @staticmethod
    async def del_by_id(id: PositiveInt, db: AsyncSession) -> None:
        await cruds.UserCrud.del_by_id(db=db, id=id)

    @staticmethod
    async def toggle_status_by_id(
        id: PositiveInt, db: AsyncSession
    ) -> schemas.UserOutSchema:
        updated_user = await cruds.UserCrud.toggle_status_by_id(db=db, id=id)

        return schemas.UserOutSchema.model_validate(updated_user)

    @staticmethod
    async def update_pwd_by_id(
        id: PositiveInt, db: AsyncSession, new_pwd: str
    ) -> schemas.UserOutSchema:
        updated_user = await cruds.UserCrud.update_pwd_by_id(
            db=db, id=id, new_pwd=new_pwd
        )

        return schemas.UserOutSchema.model_validate(updated_user)
