from typing import Annotated

from fastapi import APIRouter, Depends, Query

from .. import deps, schemas, services, utils

billing_router = APIRouter(prefix="/cobranca", tags=["Cobrança"])


@billing_router.get(
    path="/faturas-abertas", summary="Obtém faturas abertas de um cliente"
)
async def get_open_invoices(
    _: Annotated[bool, Depends(deps.get_creds)],
    # IDs NonNegativeInt, because IXC
    id_contrato: Annotated[int, Query(ge=0, description="ID do contrato")],
    pagina: utils.Page = 1,
    itens_por_pagina: utils.ItemsPerPage = 15,
) -> schemas.ListOutSchema[schemas.InvoiceOutSchema]:
    """
    Obtém faturas abertas de um cliente, através de protocolo de atendimento ou CPF/CNPJ
    """
    return await services.FinanceService.get_open_invoices(
        contract_id=id_contrato,
        page=pagina,
        items_per_page=itens_por_pagina,
    )


@billing_router.get(
    path="/faturas-vencidas", summary="Obtém faturas vencidas de um cliente"
)
async def get_overdue_invoices(
    _: Annotated[bool, Depends(deps.get_creds)],
    # IDs NonNegativeInt, because IXC
    id_contrato: Annotated[int, Query(ge=0, description="ID do contrato")],
    pagina: utils.Page = 1,
    itens_por_pagina: utils.ItemsPerPage = 15,
) -> schemas.ListOutSchema[schemas.InvoiceOutSchema]:
    """
    Obtém faturas vencidas de um cliente, através de protocolo de atendimento ou CPF/CNPJ
    """
    return await services.BillingService.get_overdue_invoices(
        contract_id=id_contrato,
        page=pagina,
        items_per_page=itens_por_pagina,
    )
