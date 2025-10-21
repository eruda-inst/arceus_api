from ..database import get_db
from typing import Optional
from pydantic import PositiveInt
from sqlalchemy.orm import Session
from .. import services, utils, schemas
from fastapi import APIRouter, Query, Path, Body, Depends


financeiro_router = APIRouter()


@financeiro_router.get(
    path="/faturas_abertas",
    response_model=schemas.FaturaAbertaListOut,
    summary="Obtém faturas associadas a um cliente, através de ID de protocolo de atendimento ou CPF/CNPJ.",
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
    page: Optional[PositiveInt] = Query(default=1, description="Número da página."),
    per_page: Optional[PositiveInt] = Query(
        ge=1, default=15, description="Itens por página."
    ),
    sortname: Optional[str] = Query(
        default="fn_areceber.id", description="Campo para ordenação."
    ),
    sortorder: Optional[utils.SortOrder] = Query(
        default=utils.SortOrder.ASC, description="Ordem da ordenação."
    ),
) -> schemas.FaturaAbertaListOut:
    """
    Obtém a lista de faturas em aberto de um cliente.

    Args:
        protocolo: O protocolo de atendimento do cliente no OpaSuite.
        cnpj_cpf: O CPF ou CNPJ do cliente.
        page: O número da página para a paginação.
        per_page: A quantidade de itens por página.
        sortname: O campo pelo qual a lista será ordenada.
        sortorder: A ordem de ordenação (ascendente ou descendente).

    Returns:
        Uma lista paginada de faturas em aberto do cliente.
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


@financeiro_router.get(
    path="/contratos",
    response_model=schemas.ComercialContratoListOut,
    summary="Obtém contratos de um cliente, por meio de ID de login.",
)
async def get_contratos(
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
        default="cliente_contrato.id", description="Campo para ordenação."
    ),
    sortorder: Optional[utils.SortOrder] = Query(
        utils.SortOrder.ASC, description="Ordem da ordenação."
    ),
) -> schemas.ComercialContratoListOut:
    """
    Obtém a lista de contratos de um cliente.

    Args:
        protocolo: O protocolo de atendimento do cliente no OpaSuite.
        cnpj_cpf: O CPF ou CNPJ do cliente.
        page: O número da página para a paginação.
        per_page: A quantidade de itens por página.
        sortname: O campo pelo qual a lista será ordenada.
        sortorder: A ordem de ordenação (ascendente ou descendente).

    Returns:
        Uma lista paginada de contratos do cliente.
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
    response_model=schemas.MensagemOut,
    summary="Realiza desbloqueio em confiança de um determinado contrato, através do ID do contrato.",
)
async def post_desbloqueio_em_confianca(
    id_contrato: PositiveInt = Query(description="ID do contrato."),
) -> schemas.MensagemOut:
    """
    Solicita o desbloqueio em confiança para um contrato.

    Args:
        id_contrato: O ID do contrato a ser desbloqueado.

    Returns:
        Uma mensagem de confirmação da solicitação.
    """
    financeiro_service = services.FinanceiroService()
    return await financeiro_service.post_desbloqueio_em_confianca(
        id_contrato=id_contrato,
    )


@financeiro_router.get(
    path="/linha_digitavel/{id_fatura}",
    response_model=schemas.LinhaDigitavelOut,
    summary="Obtém linha digitável de uma fatura, através do ID da fatura.",
)
async def get_linha_digitavel(
    id_fatura: PositiveInt = Path(ge=1, description="ID da fatura."),
) -> schemas.LinhaDigitavelOut:
    """
    Obtém a linha digitável de uma fatura específica.

    Args:
        id_fatura: O ID da fatura.

    Returns:
        A linha digitável da fatura.
    """
    financeiro_service = services.FinanceiroService()
    return await financeiro_service.get_linha_digitavel(id_fatura=id_fatura)


@financeiro_router.get(
    path="/chave_pix",
    response_model=schemas.ChavePixBase,
    summary="Obtém chave pix de uma fatura, através do ID da fatura.",
)
async def get_chave_pix(
    id_fatura: PositiveInt = Query(ge=1, description="ID da fatura.")
) -> schemas.ChavePixBase:
    """
    Obtém a chave PIX para pagamento de uma fatura.

    Args:
        id_fatura: O ID da fatura.

    Returns:
        A chave PIX da fatura.
    """
    financeiro_service = services.FinanceiroService()
    return await financeiro_service.get_chave_pix(id_fatura=id_fatura)


@financeiro_router.get(
    path="/credenciais",
    response_model=schemas.CredencialOut,
    summary="Obtém credenciais de acesso à central do assinante de um cliente, através de protocolo de atendimento.",
)
async def get_credenciais(
    protocolo: str = Query(
        min_length=12,
        max_length=12,
        description="Protocolo de atendimento do cliente no OpaSuite.",
    ),
) -> schemas.CredencialOut:
    """
    Obtém as credenciais de acesso à central do assinante de um cliente.

    Args:
        protocolo: O protocolo de atendimento do cliente no OpaSuite.

    Returns:
        As credenciais de acesso do cliente.
    """
    financeiro_service = services.FinanceiroService()
    return await financeiro_service.get_credenciais(protocolo=protocolo)


# Por razões de limitações na plataforma opa, o verbo deve ser put, ao invés de patch
@financeiro_router.put(
    path="/credenciais/{id_cliente}",
    response_model=schemas.MensagemOut,
    summary="Atualiza credenciais de acesso à central do assinante de um cliente, através do ID do cliente.",
)
async def put_credenciais(
    id_cliente: PositiveInt = Path(ge=1, description="ID do cliente."),
    credenciais: schemas.CredencialUpdate = Body(
        description="Credenciais a serem atualizadas."
    ),
) -> schemas.MensagemOut:
    """
    Atualiza as credenciais de acesso à central do assinante de um cliente.

    Args:
        id_cliente: O ID do cliente a ser atualizado.
        credenciais: As novas credenciais do cliente.

    Returns:
        Uma mensagem de confirmação da atualização.
    """
    financeiro_service = services.FinanceiroService()
    return await financeiro_service.put_credenciais(
        id_cliente=id_cliente, credenciais=credenciais
    )


@financeiro_router.get(
    path="/ultima_fatura_paga",
    response_model=schemas.FaturaPagaBase,
    summary="Obtém última fatura paga de um contrato, através do ID do contrato.",
)
async def get_ultima_fatura_paga(
    id_contrato: PositiveInt = Query(ge=1, description="ID do contrato.")
) -> schemas.FaturaPagaBase:
    """
    Obtém a última fatura paga de um contrato.

    Args:
        id_contrato: O ID do contrato.

    Returns:
        Os dados da última fatura paga.
    """
    financeiro_service = services.FinanceiroService()
    return await financeiro_service.get_ultima_fatura_paga(id_contrato=id_contrato)
