from fastapi import APIRouter
from .routers import (
    suporte_router,
    comercial_router,
    financeiro_router,
    triagem_router,
    cobranca_router,
)

api_v1_router = APIRouter()

api_v1_router.include_router(router=suporte_router, prefix="/suporte", tags=["Suporte"])
api_v1_router.include_router(
    router=comercial_router, prefix="/comercial", tags=["Comercial"]
)
api_v1_router.include_router(
    router=financeiro_router, prefix="/financeiro", tags=["Financeiro"]
)
api_v1_router.include_router(router=triagem_router, prefix="/triagem", tags=["Triagem"])
api_v1_router.include_router(
    router=cobranca_router, prefix="/cobranca", tags=["Cobrança"]
)
