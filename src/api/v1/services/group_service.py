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
    ) -> schemas.GroupOut:
        grupo = await cruds.GroupCrud.get_by(
            db=db, id=id, nome=nome, id_usuario=id_usuario
        )

        return schemas.GroupOut.model_validate(grupo)

    @staticmethod
    async def get_all(db: AsyncSession) -> schemas.ListOut[schemas.GroupOut]:
        total_items, groups = await cruds.GroupCrud.get_all(db=db)

        return schemas.ListOut[schemas.GroupOut](
            data=[schemas.GroupOut.model_validate(g) for g in groups],
            meta=schemas.MetaOut(
                pagina_atual=1,
                itens_por_pagina=10,
                total_itens=total_items,
            ),
        )
