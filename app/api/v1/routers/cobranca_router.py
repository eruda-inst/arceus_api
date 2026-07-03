from typing import Annotated
from .. import services, schemas
from fastapi import APIRouter, Query

cobranca_router = APIRouter(prefix="/cobranca", tags=["Cobrança"])

Protocolo = Annotated[
    str,
    Query(min_length=12, max_length=12, description="Protocolo de atendimento."),
]
CnpjCpf = Annotated[str, Query(description="CPF ou CNPJ do cliente.")]
Pagina = Annotated[int, Query(ge=1, description="Número da página.")]
ItensPorPagina = Annotated[int, Query(ge=1, description="Itens por página.")]


@cobranca_router.get(
    path="/faturas_abertas", summary="Obtém faturas abertas de um cliente."
)
async def get_faturas_abertas(
    protocolo: Protocolo | None = None,
    cnpj_cpf: CnpjCpf | None = None,
    pagina: Pagina | None = 1,
    itens_por_pagina: ItensPorPagina = 15,
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


@cobranca_router.get(
    path="/faturas_vencidas", summary="Obtém faturas vencidas de um cliente."
)
async def get_faturas_vencidas(
    protocolo: Protocolo | None = None,
    cnpj_cpf: CnpjCpf | None = None,
    pagina: Pagina | None = 1,
    itens_por_pagina: ItensPorPagina = 15,
) -> schemas.FaturaAbertaListOut:
    """
    Obtém faturas vencidas de um cliente, através de protocolo de atendimento ou CPF/CNPJ.
    """
    return await services.CobrancaService.get_faturas_vencidas(
        protocolo=protocolo,
        cnpj_cpf=cnpj_cpf,
        pagina=pagina,
        itens_por_pagina=itens_por_pagina,
    )
