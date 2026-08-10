from pydantic import PositiveInt
from sqlalchemy.ext.asyncio import AsyncSession

from .. import cruds, schemas


class PermService:
    @staticmethod
    async def get_by(
        db: AsyncSession,
        id: PositiveInt | None = None,
        nome: str | None = None,
        codigo: str | None = None,
        load_grupos: bool = False,
    ) -> schemas.PermOutSchema:
        perm = await cruds.PermCrud.get_by(
            db=db, id=id, nome=nome, codigo=codigo, load_grupos=load_grupos
        )

        return schemas.PermOutSchema.model_validate(perm)

    @staticmethod
    async def get_all_by(
        db: AsyncSession,
        id_grupo: PositiveInt | None = None,
        id_usuario: PositiveInt | None = None,
    ) -> schemas.ListOutSchema[schemas.PermOutSchema]:
        total_items, perms = await cruds.PermCrud.get_all_by(
            db=db, id_grupo=id_grupo, id_usuario=id_usuario
        )

        return schemas.ListOutSchema[schemas.PermOutSchema](
            data=[schemas.PermOutSchema.model_validate(p) for p in perms],
            meta=schemas.MetaOutSchema(
                itens_por_pagina=10, total_itens=total_items, pagina_atual=1
            ),
        )
