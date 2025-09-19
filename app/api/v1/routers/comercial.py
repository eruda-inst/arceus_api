from fastapi import APIRouter, Query
from ..services import ComercialService


router = APIRouter()
service = ComercialService()

@router.get("/status_acesso")
async def get_status_acesso(
    id_contrato: int = Query(
        ge=1,
        description="ID do contrato.",
    ),
):
    return await service.get_status_acesso(
        id_contrato=id_contrato,
    )