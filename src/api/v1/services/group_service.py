from pydantic import PositiveInt
from sqlalchemy.ext.asyncio import AsyncSession

from .. import cruds, schemas


class GroupService:
    @staticmethod
    async def get_by(
        db: AsyncSession,
        id: PositiveInt | None = None,
        nome: str | None = None,
        id_usuario: PositiveInt | None = None,
    ) -> schemas.GroupOutSchema:
        grupo = await cruds.GroupCrud.get_by(
            db=db, id=id, nome=nome, id_usuario=id_usuario
        )

        return schemas.GroupOutSchema.model_validate(grupo)

    @staticmethod
    async def get_all(
        db: AsyncSession,
    ) -> schemas.ListOutSchema[schemas.GroupOutSchema]:
        total_items, groups = await cruds.GroupCrud.get_all(db=db)

        return schemas.ListOutSchema[schemas.GroupOutSchema](
            data=[schemas.GroupOutSchema.model_validate(g) for g in groups],
            meta=schemas.MetaOutSchema(
                pagina_atual=1,
                itens_por_pagina=10,
                total_itens=total_items,
            ),
        )
