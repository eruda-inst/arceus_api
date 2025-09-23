from typing import Optional
from ..utils import SortOrder
from fastapi import APIRouter, Query, status, Body
from ..services import ComercialService
from ..schemas import ComercialContratoListOut, StatusAcessoOut, LeadIn, LeadCreate

router = APIRouter()
service = ComercialService()


@router.get(
    path="/status_acesso",
    response_model=StatusAcessoOut,
    summary="Obtém status de acesso, através de ID de contrato.",
)
async def get_status_acesso(
    id_contrato: int = Query(ge=1, description="ID do contrato.")
) -> StatusAcessoOut:
    return await service.get_status_acesso(id_contrato=id_contrato)


@router.get(
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
    page: Optional[int] = 1,
    per_page: Optional[int] = 10,
    sortname: Optional[str] = "cliente_contrato.id",
    sortorder: Optional[SortOrder] = SortOrder.ASC,
) -> ComercialContratoListOut:
    return await service.get_contratos(
        protocolo=protocolo,
        page=page,
        per_page=per_page,
        sortname=sortname,
        sortorder=sortorder,
    )


@router.post(
    path="/leads",
    status_code=status.HTTP_201_CREATED,
    response_model=LeadCreate,
    summary="Cadastra novo lead, a partir de lead submetido.",
)
async def post_lead(
    lead: LeadIn = Body(description="Lead a ser cadastrado."),
) -> LeadCreate:
    return await service.post_lead(lead=lead)
