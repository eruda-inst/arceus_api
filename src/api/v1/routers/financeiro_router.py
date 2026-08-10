from typing import Annotated

from fastapi import APIRouter, Body, Path, Query

from .. import schemas, services, utils

financeiro_router = APIRouter(prefix="/financeiro", tags=["Financeiro"])


@financeiro_router.get(
    path="/faturas_abertas", summary="Obtém faturas abertas de um cliente"
)
async def get_faturas_abertas(
    protocolo: utils.Protocolo | None = None,
    cnpj_cpf: utils.CnpjCpf | None = None,
    pagina: utils.Pagina | None = 1,
    itens_por_pagina: utils.ItensPorPagina | None = 15,
) -> schemas.ListOutSchema[schemas.FaturaOutSchema]:
    """
    Obtém faturas abertas de um cliente, através de protocolo de atendimento ou CPF/CNPJ
    """
    return await services.FinanceiroService.get_faturas_abertas(
        protocolo=protocolo,
        cnpj_cpf=cnpj_cpf,
        pagina=pagina,
        itens_por_pagina=itens_por_pagina,
    )


@financeiro_router.get(path="/contratos", summary="Obtém contratos de um cliente")
async def get_contratos(
    protocolo: utils.Protocolo | None = None,
    cnpj_cpf: utils.CnpjCpf | None = None,
    pagina: utils.Pagina | None = 1,
    itens_por_pagina: utils.ItensPorPagina | None = 10,
) -> schemas.ListOutSchema[schemas.ComercialContratoOutSchema]:
    """
    Obtém contratos de um cliente, através de protocolo de atendimento ou CPF/CNPJ
    """
    return await services.ComercialService.get_contratos(
        protocolo=protocolo,
        cnpj_cpf=cnpj_cpf,
        pagina=pagina,
        itens_por_pagina=itens_por_pagina,
    )


@financeiro_router.get(
    path="/linha_digitavel/{id_fatura}", summary="Obtém linha digitável de uma fatura"
)
async def get_linha_digitavel(
    # IDs NonNegativeInt, pois o IXC é quebrado
    id_fatura: Annotated[int, Path(ge=0, description="ID da fatura")],
) -> schemas.LinhaDigitavelOutSchema:
    """
    Obtém linha digitável de uma fatura, através do ID dela
    """
    return await services.FinanceiroService.get_linha_digitavel(id_fatura=id_fatura)


@financeiro_router.get(path="/chave_pix", summary="Obtém chave pix de uma fatura")
async def get_chave_pix(
    # IDs NonNegativeInt, pois o IXC é quebrado
    id_fatura: Annotated[int, Query(ge=0, description="ID da fatura")],
) -> schemas.ChavePixOutSchema:
    """
    Obtém chave pix de uma fatura, através do ID dela
    """
    return await services.FinanceiroService.get_chave_pix(id_fatura=id_fatura)


@financeiro_router.get(
    path="/credenciais",
    summary="Obtém credenciais da central do assinante de um cliente",
)
async def get_credenciais(
    protocolo: utils.Protocolo | None = None, cnpj_cpf: utils.CnpjCpf | None = None
) -> schemas.CredencialOutSchema:
    """
    Obtém credenciais da central do assinante de um cliente, através de protocolo de atendimento ou CPF/CNPJ
    """
    return await services.FinanceiroService.get_credenciais(
        protocolo=protocolo, cnpj_cpf=cnpj_cpf
    )


@financeiro_router.post(
    path="/desbloqueio_em_confianca",
    summary="Realiza desbloqueio em confiança de um cliente",
)
async def post_desbloqueio_em_confianca(
    # IDs NonNegativeInt, pois o IXC é quebrado
    id_contrato: Annotated[int, Query(ge=0, description="ID do contrato")],
) -> schemas.MensagemOutSchema:
    """
    Realiza desbloqueio em confiança de um cliente, através do id do contrato
    """
    return await services.FinanceiroService.post_desbloqueio_em_confianca(
        id_contrato=id_contrato,
    )


# Por razões de limitações na plataforma opa, o verbo deve ser put, ao invés de patch
@financeiro_router.put(
    path="/credenciais/{id_cliente}",
    summary="Atualiza senha da central do assinante de um cliente",
)
async def put_credenciais(
    # IDs NonNegativeInt, pois o IXC é quebrado
    id_cliente: Annotated[int, Path(ge=0, description="ID do cliente")],
    senha: Annotated[str, Body(embed=True, description="Nova senha")],
) -> schemas.CredencialOutSchema:
    """
    Atualiza senha da central do assinante de um cliente, através do id do cliente
    """
    return await services.FinanceiroService.put_credenciais(
        id_cliente=id_cliente, senha=senha
    )
