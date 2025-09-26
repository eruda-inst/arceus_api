from typing import Optional
from ..utils import SortOrder
from pydantic import PositiveInt
from fastapi import APIRouter, Query
from ..services import FinanceiroService
from ..schemas import FaturaOut


financeiro_router = APIRouter()
financeiro_service = FinanceiroService()


@financeiro_router.get(
    path="/faturas",
    response_model=FaturaOut,
    summary="Obtém faturas associadas a um cliente, através de ID de protocolo de atendimento.",
)
async def get_faturas(
    protocolo: str = Query(
        min_length=12,
        max_length=12,
        description="Protocolo de atendimento do cliente no OpaSuite.",
    ),
    page: Optional[PositiveInt] = Query(default=1, description="Número da página."),
    per_page: Optional[PositiveInt] = Query(
        default=10, description="Itens por página."
    ),
    sortname: Optional[str] = Query(
        default="fn_areceber.id", description="Campo para ordenação."
    ),
    sortorder: Optional[SortOrder] = Query(
        default=SortOrder.ASC, description="Ordem da ordenação."
    ),
) -> FaturaOut:
    return await financeiro_service.get_faturas(
        protocolo=protocolo,
        page=page,
        per_page=per_page,
        sortname=sortname,
        sortorder=sortorder,
    )
