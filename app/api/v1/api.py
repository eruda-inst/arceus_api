from fastapi import APIRouter
from .routers import suporte_router, comercial_router, financeiro_router

router = APIRouter()

router.include_router(router=suporte_router, prefix="/suporte", tags=["Suporte"])
router.include_router(router=comercial_router, prefix="/comercial", tags=["Comercial"])
router.include_router(
    router=financeiro_router, prefix="/financeiro", tags=["Financeiro"]
)
