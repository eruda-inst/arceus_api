from typing import Optional
from pydantic import PositiveInt
from fastapi import APIRouter, Query, Path
from .. import services, utils, schemas


financeiro_router = APIRouter()
financeiro_service = services.FinanceiroService()
comercial_service = services.ComercialService()


@financeiro_router.get(
    path="/faturas_abertas",
    response_model=schemas.FaturaAbertaListOut,
    summary="Obtém faturas associadas a um cliente, através de ID de protocolo de atendimento.",
)
async def get_faturas_abertas(
    protocolo: str = Query(
        min_length=12,
        max_length=12,
        description="Protocolo de atendimento do cliente no OpaSuite.",
    ),
    page: Optional[PositiveInt] = Query(default=1, description="Número da página."),
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
        page=page,
        per_page=per_page,
        sortname=sortname,
        sortorder=sortorder,
    )


@financeiro_router.get(
    path="/contratos",
    response_model=schemas.ComercialContratoListOut,
    summary="Obtém contratos de um cliente, por meio de ID de login.",
)
async def get_contratos(
    protocolo: str = Query(
        min_length=12,
        max_length=12,
        description="Protocolo de atendimento do cliente no OpaSuite.",
    ),
    page: Optional[PositiveInt] = Query(
        ge=1, default=1, description="Número da página."
    ),
    per_page: Optional[PositiveInt] = Query(
        ge=1, default=10, description="Itens por página."
    ),
    sortname: Optional[str] = Query(
        default="cliente_contrato.id", description="Campo para ordenação."
    ),
    sortorder: Optional[utils.SortOrder] = Query(
        utils.SortOrder.ASC, description="Ordem da ordenação."
    ),
) -> schemas.ComercialContratoListOut:
    return await comercial_service.get_contratos(
        protocolo=protocolo,
        page=page,
        per_page=per_page,
        sortname=sortname,
        sortorder=sortorder,
    )


@financeiro_router.post(
    path="/desbloqueio_em_confianca",
    response_model=schemas.MensagemOut,
    summary="Realiza desbloqueio em confiança de um determinado contrato, através do ID do contrato.",
)
async def post_desbloqueio_em_confianca(
    id_contrato: PositiveInt = Query(description="ID do contrato."),
) -> schemas.MensagemOut:
    return await financeiro_service.post_desbloqueio_em_confianca(
        id_contrato=id_contrato
    )


@financeiro_router.get(
    path="/linha_digitavel/{id}",
    response_model=schemas.LinhaDigitavelOut,
    summary="Obtém linha digitável de uma fatura, através do ID da fatura.",
)
async def get_linha_digitavel(
    id: PositiveInt = Path(ge=1, description="ID da fatura.")
) -> schemas.LinhaDigitavelOut:
    return await financeiro_service.get_linha_digitavel(id=id)


@financeiro_router.get(
    path="/chave_pix",
    response_model=schemas.ChavePixBase,
    summary="Obtém chave pix de uma fatura, através do ID da fatura.",
)
async def get_chave_pix(
    id_fatura: PositiveInt = Query(ge=1, description="ID da fatura."),
) -> schemas.ChavePixBase:
    return await financeiro_service.get_chave_pix(id_fatura=id_fatura)


@financeiro_router.get(path="/credenciais/{id}")
async def get_credenciais(
    id: PositiveInt = Path(ge=1, description="ID do cliente."),
) -> schemas.CredenciaisOut:
    return await financeiro_service.get_credenciais(id=id)
