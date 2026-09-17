from typing import Annotated

from fastapi import APIRouter, Depends, Query

from .. import deps, schemas, services, utils

upgrade_router = APIRouter(prefix="/upgrade", tags=["Upgrade"])


@upgrade_router.get(
    path="/planos-sugeridos",
    summary="Sugere planos oficiais de acordo com planos desatualizados",
)
async def get_suggested_plans(
    _: Annotated[bool, Depends(deps.get_creds)],
    # IDs NonNegativeInt, pois o IXC é quebrado
    id_cliente: Annotated[int, Query(get=0, description="ID do cliente no IXC")],
    pagina: utils.Page = 1,
    itens_por_pagina: utils.ItemsPerPage = 10,
) -> schemas.ListOutSchema[schemas.SuggestedPlanOutSchema]:
    """
    Sugere planos de venda oficiais de acordo com planos de venda desatualizados, para cada cadastro associado a um cliente
    """
    return await services.UpgradeService.get_suggested_plans(
        customer_id=id_cliente, page=pagina, items_per_page=itens_por_pagina
    )
