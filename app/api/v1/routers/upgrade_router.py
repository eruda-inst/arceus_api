from typing import Annotated
from fastapi import APIRouter, Query
from .. import services, schemas, utils

upgrade_router = APIRouter(prefix="/upgrade", tags=["Upgrade"])


@upgrade_router.get(
    path="/planos_sugeridos",
    summary="Sugere planos oficiais de acordo com planos desatualizados.",
)
async def get_planos_sugeridos(
    id_cliente: Annotated[int, Query(get=1, description="ID do cliente no IXC.")],
    page: Annotated[int | None, Query(ge=1, description="Número da página.")] = 1,
    per_page: Annotated[int | None, Query(ge=1, description="Itens por página.")] = 10,
    sort_name: Annotated[
        str | None, Query(description="Campo para ordenação.")
    ] = "cliente_contrato.id",
    sort_order: Annotated[
        utils.SortOrder | None, Query(description="Ordem da ordenação.")
    ] = utils.SortOrder.ASC,
) -> schemas.PlanoSugeridoListOut:
    """
    Sugere planos de venda oficiais de acordo com planos de venda desatualizados, para cada cadastro associado a um cliente.
    """
    return await services.UpgradeService.get_planos_sugeridos(
        id_cliente=id_cliente,
        page=page,
        per_page=per_page,
        sort_name=sort_name,
        sort_order=sort_order,
    )
