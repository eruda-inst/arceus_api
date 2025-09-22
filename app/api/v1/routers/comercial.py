from fastapi import APIRouter, Query
from ..schemas import StatusAcessoOut
from ..services import ComercialService


router = APIRouter()
service = ComercialService()


@router.get(
    path="/status_acesso",
    description="Obtém status de acesso, através de ID de contrato.",
)
async def get_status_acesso(
    id_contrato: int = Query(ge=1, description="ID do contrato."),
) -> StatusAcessoOut:
    return await service.get_status_acesso(id_contrato=id_contrato)
