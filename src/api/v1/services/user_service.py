from pydantic import PositiveInt
from sqlalchemy.ext.asyncio import AsyncSession

from .. import cruds, schemas, services


class UserService:
    @staticmethod
    async def create(db: AsyncSession, data: schemas.UserIn) -> schemas.UserOut:
        # Only users that exist in the external IXC system are allowed to be created locally.
        # If get_by_email() does not find the user, it raises a "not found" exception,
        # which prevents the local user from being created.
        _ = await services.IXCUserService.get_by_email(email=data.email)

        created_user = await cruds.UserCrud.create(db=db, data=data)

        return schemas.UserOut.model_validate(created_user)

    @staticmethod
    async def get_all_by(
        db: AsyncSession,
        page: PositiveInt,
        items_per_page: PositiveInt,
        name: str | None = None,
        email: str | None = None,
        active: bool | None = None,
        group_id: PositiveInt | None = None,
    ) -> schemas.ListOut[schemas.UserOut]:
        total_items, users = await cruds.UserCrud.get_all_by(
            db=db,
            page=page,
            items_per_page=items_per_page,
            name=name,
            email=email,
            active=active,
            group_id=group_id,
        )

        return schemas.ListOut[schemas.UserOut](
            data=[schemas.UserOut.model_validate(u) for u in users],
            meta=schemas.MetaOut(
                pagina_atual=page,
                itens_por_pagina=items_per_page,
                total_itens=total_items,
            ),
        )

    @staticmethod
    async def del_by_id(id: PositiveInt, db: AsyncSession) -> None:
        await cruds.UserCrud.del_by_id(db=db, id=id)

    @staticmethod
    async def toggle_status_by_id(id: PositiveInt, db: AsyncSession) -> schemas.UserOut:
        updated_user = await cruds.UserCrud.toggle_status_by_id(db=db, id=id)

        return schemas.UserOut.model_validate(updated_user)

    @staticmethod
    async def update_pwd_by_id(
        id: PositiveInt, db: AsyncSession, new_pwd: str
    ) -> schemas.UserOut:
        updated_user = await cruds.UserCrud.update_pwd_by_id(
            db=db, id=id, new_pwd=new_pwd
        )

        return schemas.UserOut.model_validate(updated_user)
