from typing import Annotated

from fastapi import APIRouter, Query

from .. import schemas, services, utils

cobranca_router = APIRouter(prefix="/cobranca", tags=["Cobrança"])


@cobranca_router.get(
    path="/faturas-abertas", summary="Obtém faturas abertas de um cliente"
)
async def get_faturas_abertas(
    # IDs NonNegativeInt, pois o IXC é quebrado
    id_contrato: Annotated[int, Query(ge=0, description="ID do contrato")],
    pagina: utils.Pagina | None = 1,
    itens_por_pagina: utils.ItensPorPagina = 15,
) -> schemas.ListOutSchema[schemas.FaturaOutSchema]:
    """
    Obtém faturas abertas de um cliente, através de protocolo de atendimento ou CPF/CNPJ
    """
    return await services.FinanceiroService.get_faturas_abertas(
        id_contrato=id_contrato,
        pagina=pagina,
        itens_por_pagina=itens_por_pagina,
    )


@cobranca_router.get(
    path="/faturas-vencidas", summary="Obtém faturas vencidas de um cliente"
)
async def get_faturas_vencidas(
    # IDs NonNegativeInt, pois o IXC é quebrado
    id_contrato: Annotated[int, Query(ge=0, description="ID do contrato")],
    pagina: utils.Pagina | None = 1,
    itens_por_pagina: utils.ItensPorPagina = 15,
) -> schemas.ListOutSchema[schemas.FaturaOutSchema]:
    """
    Obtém faturas vencidas de um cliente, através de protocolo de atendimento ou CPF/CNPJ
    """
    return await services.CobrancaService.get_faturas_vencidas(
        id_contrato=id_contrato,
        pagina=pagina,
        itens_por_pagina=itens_por_pagina,
    )
