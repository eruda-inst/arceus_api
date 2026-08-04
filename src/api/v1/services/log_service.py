from pydantic import PositiveInt
from sqlalchemy.ext.asyncio import AsyncSession

from .. import cruds, schemas


class LogService:
    @staticmethod
    async def get_all(
        db: AsyncSession,
        page: PositiveInt,
        items_per_page: PositiveInt,
        metodo: str | None = None,
        endpoint: str | None = None,
        codigo: PositiveInt | None = None,
        data_inicio: str | None = None,
        data_fim: str | None = None,
        hora_inicio: str | None = None,
        hora_fim: str | None = None,
        protocolo: str | None = None,
        setor: str | None = None,
        nome_cliente: str | None = None,
    ) -> schemas.ListOut[schemas.LogOut]:
        total_items, logs = await cruds.LogCrud.get_all(
            db=db,
            page=page,
            items_per_page=items_per_page,
            metodo=metodo,
            endpoint=endpoint,
            codigo=codigo,
            data_inicio=data_inicio,
            data_fim=data_fim,
            hora_inicio=hora_inicio,
            hora_fim=hora_fim,
            protocolo=protocolo,
            setor=setor,
            nome_cliente=nome_cliente,
        )

        total_paginas = (total_items + items_per_page - 1) // items_per_page

        return schemas.ListOut[schemas.LogOut](
            data=[schemas.LogOut.model_validate(log) for log in logs],
            meta=schemas.MetaOut(
                itens_por_pagina=items_per_page,
                pagina_atual=page,
                total_itens=total_items,
                total_paginas=total_paginas,
            ),
        )
