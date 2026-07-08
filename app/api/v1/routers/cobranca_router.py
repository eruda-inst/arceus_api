from fastapi import APIRouter
from .. import services, schemas, utils

cobranca_router = APIRouter(prefix="/cobranca", tags=["Cobrança"])


@cobranca_router.get(
    path="/faturas_abertas", summary="Obtém faturas abertas de um cliente."
)
async def get_faturas_abertas(
    protocolo: utils.Protocolo | None = None,
    cnpj_cpf: utils.CnpjCpf | None = None,
    pagina: utils.Pagina | None = 1,
    itens_por_pagina: utils.ItensPorPagina = 15,
) -> schemas.FaturaListOut:
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
    protocolo: utils.Protocolo | None = None,
    cnpj_cpf: utils.CnpjCpf | None = None,
    pagina: utils.Pagina | None = 1,
    itens_por_pagina: utils.ItensPorPagina = 15,
) -> schemas.FaturaListOut:
    """
    Obtém faturas vencidas de um cliente, através de protocolo de atendimento ou CPF/CNPJ.
    """
    return await services.CobrancaService.get_faturas_vencidas(
        protocolo=protocolo,
        cnpj_cpf=cnpj_cpf,
        pagina=pagina,
        itens_por_pagina=itens_por_pagina,
    )
