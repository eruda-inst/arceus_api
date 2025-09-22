from typing import Optional
from ..utils import SortOrder
from fastapi import APIRouter, Query
from ..services import ComercialService
from ..schemas import ComercialContratoListOut, StatusAcessoOut


router = APIRouter()
service = ComercialService()


@router.get(
    path="/status_acesso",
    description="Obtém status de acesso, através de ID de contrato.",
)
async def get_status_acesso(
    id_contrato: int = Query(ge=1, description="ID do contrato.")
) -> StatusAcessoOut:
    return await service.get_status_acesso(id_contrato=id_contrato)


@router.get(
    path="/contratos",
    description="Obtém contratos de um cliente, por meio de ID de login.",
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
):
    return await service.get_contratos(
        protocolo=protocolo,
        page=page,
        per_page=per_page,
        sortname=sortname,
        sortorder=sortorder,
    )
