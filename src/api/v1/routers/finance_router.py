"""
Router for financial endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query

from .. import deps, schemas, services, utils

finance_router = APIRouter(prefix="/financeiro", tags=["Financeiro"])


@finance_router.get(path="/chave-pix", summary="Obtém chave pix de uma fatura")
async def get_pix_key(
    _: Annotated[bool, Depends(deps.get_creds)],
    # IDs NonNegativeInt, pois o IXC é quebrado
    id_fatura: Annotated[int, Query(ge=0, description="ID da fatura")],
) -> schemas.PixKeyOutSchema:
    """
    Obtém chave pix de uma fatura, através do ID dela
    """
    return await services.FinanceService.get_pix_key(invoice_id=id_fatura)


@finance_router.get(
    path="/credenciais/{id_cliente}",
    summary="Obtém credenciais da central do assinante de um cliente",
)
async def get_credentials(
    _: Annotated[bool, Depends(deps.get_creds)],
    # IDs NonNegativeInt, pois o IXC é quebrado
    id_cliente: Annotated[int, Path(description="ID do cliente")],
) -> schemas.CredentialOutSchema:
    """
    Obtém credenciais da central do assinante de um cliente, através de ID do cliente
    """
    return await services.FinanceService.get_credentials(customer_id=id_cliente)


@finance_router.patch(
    path="/credenciais/{id_cliente}",
    summary="Atualiza senha da central do assinante de um cliente",
)
async def patch_credentials(
    _: Annotated[bool, Depends(deps.get_creds)],
    # IDs NonNegativeInt, pois o IXC é quebrado
    id_cliente: Annotated[int, Path(ge=0, description="ID do cliente")],
    senha: Annotated[str, Body(embed=True, description="Nova senha")],
) -> schemas.CredentialOutSchema:
    """
    Atualiza senha da central do assinante de um cliente, através do id do cliente
    """
    return await services.FinanceService.patch_credentials(
        customer_id=id_cliente, password=senha
    )


@finance_router.post(
    path="/desbloqueio-em-confianca",
    summary="Realiza desbloqueio em confiança de um cliente",
)
async def post_trusted_unlock(
    _: Annotated[bool, Depends(deps.get_creds)],
    # IDs NonNegativeInt, pois o IXC é quebrado
    id_contrato: Annotated[int, Query(ge=0, description="ID do contrato")],
) -> schemas.MessageOutSchema:
    """
    Realiza desbloqueio em confiança de um cliente, através do id do contrato
    """
    return await services.FinanceService.post_trusted_unlock(
        contract_id=id_contrato,
    )


@finance_router.get(
    path="/faturas-abertas", summary="Obtém faturas abertas de um cliente"
)
async def get_open_invoices(
    _: Annotated[bool, Depends(deps.get_creds)],
    # IDs NonNegativeInt, pois o IXC é quebrado
    id_contrato: Annotated[int, Query(ge=0, description="ID do contrato")],
    pagina: utils.Page = 1,
    itens_por_pagina: utils.ItemsPerPage = 15,
) -> schemas.ListOutSchema[schemas.InvoiceOutSchema]:
    """
    Obtém faturas abertas de um cliente, através do ID do contrato
    """
    return await services.FinanceService.get_open_invoices(
        contract_id=id_contrato,
        page=pagina,
        items_per_page=itens_por_pagina,
    )


@finance_router.get(
    path="/linha-digitavel/{id_fatura}", summary="Obtém linha digitável de uma fatura"
)
async def get_digitable_line(
    _: Annotated[bool, Depends(deps.get_creds)],
    # IDs NonNegativeInt, pois o IXC é quebrado
    id_fatura: Annotated[int, Path(ge=0, description="ID da fatura")],
) -> schemas.DigitableLineOutSchema:
    """
    Obtém linha digitável de uma fatura, através do ID dela
    """
    return await services.FinanceService.get_digitable_line(invoice_id=id_fatura)


@finance_router.get(
    path="/tres-faturas-abertas", summary="Obtém 3 faturas abertas de um cliente"
)
async def get_3_open_invoices(
    _: Annotated[bool, Depends(deps.get_creds)],
    # IDs NonNegativeInt, pois o IXC é quebrado
    id_contrato: Annotated[int, Query(ge=0, description="ID do contrato")],
    pagina: utils.Page = 1,
    itens_por_pagina: utils.ItemsPerPage = 15,
) -> schemas.ListOutSchema[schemas.InvoiceOutSchema]:
    """
    Obtém faturas 3 abertas de um cliente, através do ID do contrato
    """
    return await services.FinanceService.get_3_open_invoices(
        contract_id=id_contrato,
        page=pagina,
        items_per_page=itens_por_pagina,
    )
