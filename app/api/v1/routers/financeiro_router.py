from typing import Annotated
from .. import services, schemas
from fastapi import APIRouter, Query, Path, Body

financeiro_router = APIRouter(prefix="/financeiro", tags=["Financeiro"])

Protocolo = Annotated[
    str,
    Query(min_length=12, max_length=12, description="Protocolo de atendimento."),
]
Pagina = Annotated[int, Query(ge=1, description="Número da página.")]
ItensPorPagina = Annotated[int, Query(ge=1, description="Itens por página.")]
CnpjCpf = Annotated[str, Query(description="CPF ou CNPJ do cliente.")]


@financeiro_router.get(
    path="/faturas_abertas", summary="Obtém faturas abertas de um cliente."
)
async def get_faturas_abertas(
    protocolo: Protocolo | None = None,
    cnpj_cpf: CnpjCpf | None = None,
    pagina: Pagina | None = 1,
    itens_por_pagina: ItensPorPagina | None = 15,
) -> schemas.FaturaAbertaListOut:
    """
    Obtém faturas abertas de um cliente, através de protocolo de atendimento ou CPF/CNPJ.
    """
    return await services.FinanceiroService.get_faturas_abertas(
        protocolo=protocolo,
        cnpj_cpf=cnpj_cpf,
        pagina=pagina,
        itens_por_pagina=itens_por_pagina,
    )


@financeiro_router.get(path="/contratos", summary="Obtém contratos de um cliente.")
async def get_contratos(
    protocolo: Protocolo | None = None,
    cnpj_cpf: CnpjCpf | None = None,
    pagina: Pagina | None = 1,
    itens_por_pagina: ItensPorPagina | None = 10,
) -> schemas.ComercialContratoListOut:
    """
    Obtém contratos de um cliente, através de protocolo de atendimento ou CPF/CNPJ.
    """
    return await services.ComercialService.get_contratos(
        protocolo=protocolo,
        cnpj_cpf=cnpj_cpf,
        pagina=pagina,
        itens_por_pagina=itens_por_pagina,
    )


@financeiro_router.post(
    path="/desbloqueio_em_confianca",
    summary="Realiza desbloqueio em confiança de um cliente.",
)
async def post_desbloqueio_em_confianca(
    id_contrato: Annotated[int, Query(ge=1, description="ID do contrato.")],
) -> schemas.MensagemOut:
    """
    Realiza desbloqueio em confiança de um cliente, através do ID do contrato.
    """
    return await services.FinanceiroService.post_desbloqueio_em_confianca(
        id_contrato=id_contrato,
    )


@financeiro_router.get(
    path="/linha_digitavel/{id_fatura}", summary="Obtém linha digitável de uma fatura."
)
async def get_linha_digitavel(
    id_fatura: Annotated[int, Path(ge=1, description="ID da fatura.")],
) -> schemas.LinhaDigitavelOut:
    """
    Obtém linha digitável de uma fatura, através do ID dela.
    """
    return await services.FinanceiroService.get_linha_digitavel(id_fatura=id_fatura)


@financeiro_router.get(path="/chave_pix", summary="Obtém chave pix de uma fatura.")
async def get_chave_pix(
    id_fatura: Annotated[int, Query(ge=1, description="ID da fatura.")],
) -> schemas.ChavePixOut:
    """
    Obtém chave pix de uma fatura, através do ID dela.
    """
    return await services.FinanceiroService.get_chave_pix(id_fatura=id_fatura)


@financeiro_router.get(
    path="/credenciais",
    summary="Obtém credenciais da central do assinante de um cliente.",
)
async def get_credenciais(
    protocolo: Protocolo | None = None, cnpj_cpf: CnpjCpf | None = None
) -> schemas.CredencialOut:
    """
    Obtém credenciais da central do assinante de um cliente, através de protocolo de atendimento ou CPF/CNPJ.
    """
    return await services.FinanceiroService.get_credenciais(
        protocolo=protocolo, cnpj_cpf=cnpj_cpf
    )


# Por razões de limitações na plataforma opa, o verbo deve ser put, ao invés de patch
@financeiro_router.put(
    path="/credenciais/{id_cliente}",
    summary="Atualiza senha da central do assinante de um cliente.",
)
async def put_credenciais(
    id_cliente: Annotated[int, Path(ge=1, description="ID do cliente.")],
    senha: Annotated[str, Body(embed=True, description="Nova senha.")],
) -> schemas.CredencialOut:
    """
    Atualiza senha da central do assinante de um cliente, através do ID do cliente.
    """
    return await services.FinanceiroService.put_credenciais(
        id_cliente=id_cliente, senha=senha
    )
