from fastapi import APIRouter

from . import routers, websockets

api_v1_router = APIRouter(prefix="/api/v1")

# HTTP
api_v1_router.include_router(router=routers.suporte_router)
api_v1_router.include_router(router=routers.comercial_router)
api_v1_router.include_router(router=routers.financeiro_router)
api_v1_router.include_router(router=routers.triagem_router)
api_v1_router.include_router(router=routers.cobranca_router)
api_v1_router.include_router(router=routers.upgrade_router)
api_v1_router.include_router(router=routers.vila_router)
api_v1_router.include_router(router=routers.authentication_router)
api_v1_router.include_router(router=routers.group_router)
api_v1_router.include_router(router=routers.perm_router)
api_v1_router.include_router(router=routers.user_router)
api_v1_router.include_router(router=routers.ixc_user_router)

# WebSockets
api_v1_router.include_router(router=websockets.metric_ws_router)
api_v1_router.include_router(router=websockets.log_ws_router)
api_v1_router.include_router(router=websockets.user_ws_router)
