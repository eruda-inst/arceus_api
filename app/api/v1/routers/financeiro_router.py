from typing import Annotated
from pydantic import PositiveInt
from .. import services, utils, schemas
from fastapi import APIRouter, Query, Path, Body

financeiro_router = APIRouter(prefix="/financeiro", tags=["Financeiro"])


@financeiro_router.get(
    path="/faturas_abertas", summary="Obtém faturas associadas a um cliente."
)
async def get_faturas_abertas(
    protocolo: Annotated[
        str | None,
        Query(min_length=12, max_length=12, description="Protocolo de atendimento."),
    ] = None,
    cnpj_cpf: Annotated[
        str | None, Query(description="CPF ou CNPJ do cliente.")
    ] = None,
    page: Annotated[PositiveInt | None, Query(description="Número da página.")] = 1,
    per_page: Annotated[
        PositiveInt | None, Query(ge=1, description="Itens por página.")
    ] = 15,
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
    financeiro_service = services.FinanceiroService()
    return await financeiro_service.get_faturas_abertas(
        protocolo=protocolo,
        cnpj_cpf=cnpj_cpf,
        page=page,
        per_page=per_page,
        sortname=sortname,
        sortorder=sortorder,
    )


@financeiro_router.get(path="/contratos", summary="Obtém contratos de um cliente.")
async def get_contratos(
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
    ] = "cliente_contrato.id",
    sortorder: Annotated[
        utils.SortOrder | None, Query(description="Ordem da ordenação.")
    ] = utils.SortOrder.ASC,
) -> schemas.ComercialContratoListOut:
    """
    Obtém contratos de todos os clientes, atravé de protocolo de atendimento ou CPF/CNPJ.
    """
    comercial_service = services.ComercialService()
    return await comercial_service.get_contratos(
        protocolo=protocolo,
        cnpj_cpf=cnpj_cpf,
        page=page,
        per_page=per_page,
        sortname=sortname,
        sortorder=sortorder,
    )


@financeiro_router.post(
    path="/desbloqueio_em_confianca",
    summary="Realiza desbloqueio em confiança de um determinado contrato.",
)
async def post_desbloqueio_em_confianca(
    id_contrato: Annotated[PositiveInt, Query(ge=1, description="ID do contrato.")],
) -> schemas.MensagemOut:
    """
    Realiza desbloqueio em confiança de um determinado contrato, atravé do ID do contrato.
    """
    financeiro_service = services.FinanceiroService()
    return await financeiro_service.post_desbloqueio_em_confianca(
        id_contrato=id_contrato,
    )


@financeiro_router.get(
    path="/linha_digitavel/{id_fatura}", summary="Obtém linha digitável de uma fatura."
)
async def get_linha_digitavel(
    id_fatura: Annotated[PositiveInt, Path(ge=1, description="ID da fatura.")],
) -> schemas.LinhaDigitavelOut:
    """
    Obtém linha digitável de uma fatura, atravé do ID da fatura.
    """
    financeiro_service = services.FinanceiroService()
    return await financeiro_service.get_linha_digitavel(id_fatura=id_fatura)


@financeiro_router.get(path="/chave_pix", summary="Obtém chave pix de uma fatura.")
async def get_chave_pix(
    id_fatura: Annotated[PositiveInt, Query(ge=1, description="ID da fatura.")],
) -> schemas.ChavePixBase:
    """
    Obtém chave pix de uma fatura, atravé do ID da fatura.
    """
    financeiro_service = services.FinanceiroService()
    return await financeiro_service.get_chave_pix(id_fatura=id_fatura)


@financeiro_router.get(
    path="/credenciais",
    summary="Obtém credenciais de acesso à central do assinante de um cliente.",
)
async def get_credenciais(
    protocolo: Annotated[
        str | None,
        Query(min_length=12, max_length=12, description="Protocolo de atendimento."),
    ] = None,
    cnpj_cpf: Annotated[
        str | None, Query(description="CPF ou CNPJ do cliente.")
    ] = None,
) -> schemas.CredencialOut:
    """
    Obtém credenciais de acesso à central do assinante de um cliente, atravé de protocolo de atendimento.
    """
    financeiro_service = services.FinanceiroService()
    return await financeiro_service.get_credenciais(
        protocolo=protocolo, cnpj_cpf=cnpj_cpf
    )


# Por razões de limitações na plataforma opa, o verbo deve ser put, ao invés de patch
@financeiro_router.put(
    path="/credenciais/{id_cliente}",
    summary="Atualiza credenciais de acesso à central do assinante de um cliente.",
)
async def put_credenciais(
    id_cliente: Annotated[PositiveInt, Path(ge=1, description="ID do cliente.")],
    credenciais: Annotated[
        schemas.CredencialUpdate, Body(description="Credenciais a serem atualizadas.")
    ],
) -> schemas.MensagemOut:
    """
    Atualiza credenciais de acesso à central do assinante de um cliente, atravé do ID do cliente.
    """
    financeiro_service = services.FinanceiroService()
    return await financeiro_service.put_credenciais(
        id_cliente=id_cliente, credenciais=credenciais
    )


@financeiro_router.get(
    path="/ultima_fatura_paga", summary="Obtém última fatura paga de um contrato."
)
async def get_ultima_fatura_paga(
    id_contrato: Annotated[PositiveInt, Query(ge=1, description="ID do contrato.")],
) -> schemas.FaturaPagaBase:
    """
    Obtém última fatura paga de um contrato, atravé do ID do contrato.
    """
    financeiro_service = services.FinanceiroService()
    return await financeiro_service.get_ultima_fatura_paga(id_contrato=id_contrato)
