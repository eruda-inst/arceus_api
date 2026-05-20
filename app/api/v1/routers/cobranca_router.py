from typing import Annotated
from pydantic import PositiveInt
from fastapi import APIRouter, Query
from .. import utils, services, schemas

cobranca_router = APIRouter(prefix="/cobranca", tags=["Cobrança"])


@cobranca_router.get(
    path="/faturas_abertas", summary="Obtém faturas abertas de um cliente."
)
async def get_faturas_abertas(
    protocolo: Annotated[
        str | None,
        Query(min_length=12, max_length=12, description="Protocolo de atendimento."),
    ] = None,
    cnpj_cpf: Annotated[
        str | None, Query(description="CPF ou CNPJ do cliente.")
    ] = None,
    page: Annotated[
        PositiveInt | None, Query(ge=1, description="Número da página.")
    ] = 1,
    per_page: Annotated[
        PositiveInt | None, Query(ge=1, description="Itens por página.")
    ] = 10,
    sortname: Annotated[
        str | None, Query(description="Campo para ordenação.")
    ] = "fn_areceber.id",
    sortorder: Annotated[
        utils.SortOrder | None, Query(description="Ordem da ordenação.")
    ] = utils.SortOrder.ASC,
) -> schemas.FaturaAbertaListOut:
    """
    Obtém faturas abertas de todos os contratos de um cliente, através de protocolo de atendimento ou CPF/CNPJ.
    """
    return await services.FinanceiroService.get_faturas_abertas(
        protocolo=protocolo,
        cnpj_cpf=cnpj_cpf,
        page=page,
        per_page=per_page,
        sortorder=sortorder,
        sortname=sortname,
    )


@cobranca_router.get(
    path="/faturas_vencidas", summary="Obtém faturas vencidas de um cliente."
)
async def get_faturas_vencidas(
    protocolo: Annotated[
        str | None,
        Query(min_length=12, max_length=12, description="Protocolo de atendimento."),
    ] = None,
    cnpj_cpf: Annotated[
        str | None, Query(description="CPF ou CNPJ do cliente.")
    ] = None,
    page: Annotated[
        PositiveInt | None, Query(ge=1, description="Número da página.")
    ] = 1,
    per_page: Annotated[
        PositiveInt | None, Query(ge=1, description="Itens por página.")
    ] = 10,
    sortname: Annotated[
        str | None, Query(description="Campo para ordenação.")
    ] = "fn_areceber.id",
    sortorder: Annotated[
        utils.SortOrder | None, Query(description="Ordem da ordenação.")
    ] = utils.SortOrder.ASC,
) -> schemas.FaturaAbertaListOut:
    """
    Obtém faturas vencidas de todos os contratos de um cliente, através de protocolo de atendimento ou CPF/CNPJ.
    """
    return await services.CobrancaService.get_faturas_vencidas(
        protocolo=protocolo,
        cnpj_cpf=cnpj_cpf,
        page=page,
        per_page=per_page,
        sortorder=sortorder,
        sortname=sortname,
    )
