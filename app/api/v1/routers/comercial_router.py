from typing import Optional
from pydantic import PositiveInt
from .. import utils, services, schemas
from fastapi import APIRouter, Query, status, Body

comercial_router = APIRouter(prefix="/comercial", tags=["Comercial"])


@comercial_router.get(
    path="/status_acesso",
    response_model=schemas.StatusAcessoOut,
    summary="Obtém status de acesso do contrato.",
    description="Obtém status de acesso de um contrato, atravé do ID do contrato.",
)
async def get_status_acesso(
    id_contrato: PositiveInt = Query(ge=1, description="ID do contrato.")
) -> schemas.StatusAcessoOut:
    comercial_service = services.ComercialService()
    return await comercial_service.get_status_acesso(id_contrato=id_contrato)


@comercial_router.get(
    path="/contratos",
    response_model=schemas.ComercialContratoListOut,
    summary="Obtém contratos de um cliente, por meio de protocolo de atendimento ou CPF/CNPJ.",
    description="Obtém contratos de todos os clientes, atravé de protocolo de atendimento ou CPF/CNPJ.",
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
    comercial_service = services.ComercialService()
    return await comercial_service.get_contratos(
        protocolo=protocolo,
        cnpj_cpf=cnpj_cpf,
        page=page,
        per_page=per_page,
        sortname=sortname,
        sortorder=sortorder,
    )


@comercial_router.post(
    path="/leads",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.LeadCreate,
    summary="Cadastra novo lead.",
    description="Cadastra novo lead e retorna o ID do lead criado.",
)
async def post_leads(
    lead: schemas.LeadIn = Body(description="Lead a ser cadastrado."),
) -> schemas.LeadCreate:
    comercial_service = services.ComercialService()
    return await comercial_service.post_leads(lead=lead)


@comercial_router.get(
    path="/cliente_existe",
    response_model=schemas.ClienteExisteOut,
    summary="Verifica se um cliente existe no Opa.",
    description="Verifica se um cliente existe no Opa, através do CPF/CNPJ.",
)
async def cliente_existe(cpf_cnpj: str) -> schemas.ClienteExisteOut:
    return await services.ComercialService.cliente_existe(cpf_cnpj=cpf_cnpj)
