from typing import Annotated

from fastapi import APIRouter, Body, Depends, Query, status

from .. import deps, schemas, services, utils

comercial_router = APIRouter(prefix="/comercial", tags=["Comercial"])


@comercial_router.get(
    path="/status-acesso", summary="Obtém status de acesso de um contrato"
)
async def get_status_acesso(
    _: Annotated[bool, Depends(deps.get_creds)],
    # IDs NonNegativeInt, pois o IXC é quebrado
    id_contrato: Annotated[int, Query(ge=0, description="ID do contrato")],
) -> schemas.StatusInternetOutSchema:
    """
    Obtém status de acesso de um contrato, através do id do contrato
    """
    return await services.ComercialService.get_status_acesso(id_contrato=id_contrato)


@comercial_router.post(
    path="/leads", status_code=status.HTTP_201_CREATED, summary="Cadastra novo lead"
)
async def post_leads(
    _: Annotated[bool, Depends(deps.get_creds)],
    lead: Annotated[schemas.LeadInSchema, Body(description="Lead a ser cadastrado")],
) -> schemas.LeadOutSchema:
    """
    Cadastra novo lead e retorna o id dele
    """
    return await services.ComercialService.post_leads(lead=lead)


@comercial_router.patch(path="/leads", summary="Atualiza lead parcialmente")
async def patch_lead(
    _: Annotated[bool, Depends(deps.get_creds)],
    cnpj_cpf: utils.CnpjCpf,
    lead: Annotated[schemas.LeadUpdateSchema, Body(description="Dados do lead")],
) -> schemas.LeadOutSchema:
    """
    Atualiza lead parcialmente, através de dados do lead
    """
    return await services.ComercialService.patch_lead(cnpj_cpf=cnpj_cpf, lead=lead)
