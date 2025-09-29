from typing import Optional
from ..utils import SortOrder
from pydantic import PositiveInt
from fastapi import APIRouter, Query, status, Body
from ..services import ComercialService
from ..schemas import (
    ComercialContratoListOut,
    StatusAcessoOut,
    LeadIn,
    LeadCreate,
)

comercial_router = APIRouter()
comercial_service = ComercialService()


@comercial_router.get(
    path="/status_acesso",
    response_model=StatusAcessoOut,
    summary="Obtém status de acesso, através de ID de contrato.",
)
async def get_status_acesso(
    id_contrato: PositiveInt = Query(ge=1, description="ID do contrato."),
) -> StatusAcessoOut:
    return await comercial_service.get_status_acesso(id_contrato=id_contrato)


@comercial_router.get(
    path="/contratos",
    response_model=ComercialContratoListOut,
    summary="Obtém contratos de um cliente, por meio de ID de login.",
)
async def get_contratos(
    protocolo: str = Query(
        min_length=12,
        max_length=12,
        description="Protocolo de atendimento do cliente no OpaSuite.",
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
    sortorder: Optional[SortOrder] = Query(
        SortOrder.ASC, description="Ordem da ordenação."
    ),
) -> ComercialContratoListOut:
    return await comercial_service.get_contratos(
        protocolo=protocolo,
        page=page,
        per_page=per_page,
        sortname=sortname,
        sortorder=sortorder,
    )


@comercial_router.post(
    path="/leads",
    status_code=status.HTTP_201_CREATED,
    response_model=LeadCreate,
    summary="Cadastra novo lead, a partir de lead submetido.",
)
async def post_leads(
    lead: LeadIn = Body(description="Lead a ser cadastrado."),
) -> LeadCreate:
    return await comercial_service.post_leads(lead=lead)
