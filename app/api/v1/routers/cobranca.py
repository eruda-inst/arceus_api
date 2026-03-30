from typing import Optional
from pydantic import PositiveInt
from fastapi import APIRouter, Query
from .. import utils, services, schemas

cobranca_router = APIRouter()
cobranca_service = services.CobrancaService()
financeiro_service = services.FinanceiroService()


@cobranca_router.get(
    path="/faturas_abertas",
    response_model=schemas.FaturaAbertaListOut,
    summary="Obtém faturas abertas de um cliente.",
    description="Obtém faturas abertas de todos os contratos de um cliente, através de protocolo de atendimento ou CPF/CNPJ.",
)
async def get_faturas_abertas(
    protocolo: Optional[str] = Query(
        default=None,
        min_length=12,
        max_length=12,
        description="Protocolo de atendimento.",
    ),
    cnpj_cpf: Optional[str] = Query(
        default=None, description="CPF ou CNPJ do cliente."
    ),
    page: Optional[PositiveInt] = Query(
        ge=1, default=1, description="Número da página."
    ),
    per_page: Optional[PositiveInt] = Query(
        ge=1, default=10, description="Itens por página."
    ),
    sortname: Optional[str] = Query(
        default="fn_areceber.id", description="Campo para ordenação."
    ),
    sortorder: Optional[utils.SortOrder] = Query(
        default=utils.SortOrder.ASC, description="Ordem da ordenação."
    ),
) -> schemas.FaturaAbertaListOut:
    return await financeiro_service.get_faturas_abertas(
        protocolo=protocolo,
        cnpj_cpf=cnpj_cpf,
        page=page,
        per_page=per_page,
        sortorder=sortorder,
        sortname=sortname,
    )


@cobranca_router.get(
    path="/faturas_vencidas",
    response_model=schemas.FaturaAbertaListOut,
    summary="Obtém faturas vencidas de um cliente.",
    description="Obtém faturas vencidas de todos os contratos de um cliente, através de protocolo de atendimento ou CPF/CNPJ.",
)
async def get_faturas_vencidas(
    protocolo: Optional[str] = Query(
        default=None,
        min_length=12,
        max_length=12,
        description="Protocolo de atendimento.",
    ),
    cnpj_cpf: Optional[str] = Query(
        default=None, description="CPF ou CNPJ do cliente."
    ),
    page: Optional[PositiveInt] = Query(
        ge=1, default=1, description="Número da página."
    ),
    per_page: Optional[PositiveInt] = Query(
        ge=1, default=10, description="Itens por página."
    ),
    sortname: Optional[str] = Query(
        default="fn_areceber.id", description="Campo para ordenação."
    ),
    sortorder: Optional[utils.SortOrder] = Query(
        default=utils.SortOrder.ASC, description="Ordem da ordenação."
    ),
):
    return await cobranca_service.get_faturas_vencidas(
        protocolo=protocolo,
        cnpj_cpf=cnpj_cpf,
        page=page,
        per_page=per_page,
        sortorder=sortorder,
        sortname=sortname,
    )
