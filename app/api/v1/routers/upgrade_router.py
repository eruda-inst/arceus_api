from typing import Annotated
from .. import services, schemas
from fastapi import APIRouter, Query

upgrade_router = APIRouter(prefix="/upgrade", tags=["Upgrade"])


@upgrade_router.get(
    path="/planos_sugeridos",
    summary="Sugere planos oficiais de acordo com planos desatualizados.",
)
async def get_planos_sugeridos(
    id_cliente: Annotated[int, Query(get=1, description="ID do cliente no IXC.")],
    pagina: Annotated[int | None, Query(ge=1, description="Número da página.")] = 1,
    itens_por_pagina: Annotated[
        int | None, Query(ge=1, description="Itens por página.")
    ] = 10,
) -> schemas.PlanoSugeridoListOut:
    """
    Sugere planos de venda oficiais de acordo com planos de venda desatualizados, para cada cadastro associado a um cliente.
    """
    return await services.UpgradeService.get_planos_sugeridos(
        id_cliente=id_cliente, page=pagina, per_page=itens_por_pagina
    )
