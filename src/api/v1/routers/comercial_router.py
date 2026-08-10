from typing import Annotated

from fastapi import APIRouter, Body, Query, status

from .. import schemas, services, utils

comercial_router = APIRouter(prefix="/comercial", tags=["Comercial"])


@comercial_router.get(
    path="/status_acesso", summary="Obtém status de acesso de um contrato"
)
async def get_status_acesso(
    # IDs NonNegativeInt, pois o IXC é quebrado
    id_contrato: Annotated[int, Query(ge=0, description="ID do contrato")],
) -> schemas.StatusInternetOutSchema:
    """
    Obtém status de acesso de um contrato, através do id do contrato
    """
    return await services.ComercialService.get_status_acesso(id_contrato=id_contrato)


@comercial_router.get(path="/contratos", summary="Obtém contratos de um cliente")
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


@comercial_router.get(
    path="/cliente_existe", summary="Checa se um cliente existe no Opa"
)
async def cliente_existe(cpf_cnpj: utils.CnpjCpf) -> schemas.ClienteExisteOutSchema:
    """
    Checa se um cliente existe no Opa, através do CPF/CNPJ
    """
    return await services.ComercialService.cliente_existe(cpf_cnpj=cpf_cnpj)


@comercial_router.post(
    path="/leads", status_code=status.HTTP_201_CREATED, summary="Cadastra novo lead"
)
async def post_leads(
    lead: Annotated[schemas.LeadInSchema, Body(description="Lead a ser cadastrado")],
) -> schemas.LeadOutSchema:
    """
    Cadastra novo lead e retorna o id dele
    """
    return await services.ComercialService.post_leads(lead=lead)


# Por razões de limitações na plataforma opa, o verbo deve ser put, ao invés de patch
@comercial_router.put(path="/leads", summary="Atualiza lead parcialmente")
async def put_lead(
    cnpj_cpf: utils.CnpjCpf,
    lead: Annotated[schemas.LeadUpdateSchema, Body(description="Dados do lead")],
) -> schemas.LeadOutSchema:
    """
    Atualiza lead parcialmente, através de dados do lead
    """
    return await services.ComercialService.put_lead(cnpj_cpf=cnpj_cpf, lead=lead)
