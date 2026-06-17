from fastapi import APIRouter
from .routers import (
    suporte_router,
    comercial_router,
    financeiro_router,
    triagem_router,
    cobranca_router,
    upgrade_router,
)

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(router=suporte_router)
api_v1_router.include_router(router=comercial_router)
api_v1_router.include_router(router=financeiro_router)
api_v1_router.include_router(router=triagem_router)
api_v1_router.include_router(router=cobranca_router)
api_v1_router.include_router(router=upgrade_router)
