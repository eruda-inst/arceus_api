from . import routers
from fastapi import APIRouter

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(router=routers.suporte_router)
api_v1_router.include_router(router=routers.comercial_router)
api_v1_router.include_router(router=routers.financeiro_router)
api_v1_router.include_router(router=routers.triagem_router)
api_v1_router.include_router(router=routers.cobranca_router)
api_v1_router.include_router(router=routers.upgrade_router)
api_v1_router.include_router(router=routers.vila_router)
