from typing import Annotated

from fastapi import APIRouter, Query

from .. import schemas, services, utils

upgrade_router = APIRouter(prefix="/upgrade", tags=["Upgrade"])


@upgrade_router.get(
    path="/planos_sugeridos",
    summary="Sugere planos oficiais de acordo com planos desatualizados",
)
async def get_planos_sugeridos(
    # IDs NonNegativeInt, pois o IXC é quebrado
    id_cliente: Annotated[int, Query(get=0, description="ID do cliente no IXC")],
    pagina: utils.Pagina | None = 1,
    itens_por_pagina: utils.ItensPorPagina | None = 10,
) -> schemas.ListOutSchema[schemas.PlanoSugeridoOutSchema]:
    """
    Sugere planos de venda oficiais de acordo com planos de venda desatualizados, para cada cadastro associado a um cliente
    """
    return await services.UpgradeService.get_planos_sugeridos(
        id_cliente=id_cliente, pagina=pagina, itens_por_pagina=itens_por_pagina
    )
