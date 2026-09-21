"""
API v1 router aggregator.

Mounts all HTTP routers and WebSocket routers under the `/api/v1` prefix.
"""

from fastapi import APIRouter

from . import routers, websockets

# Main API v1 router with the versioned prefix
api_v1_router = APIRouter(prefix="/api/v1")

# HTTP department routers
api_v1_router.include_router(router=routers.billing_router)
api_v1_router.include_router(router=routers.sales_router)
api_v1_router.include_router(router=routers.finance_router)
api_v1_router.include_router(router=routers.support_router)
api_v1_router.include_router(router=routers.triage_router)
api_v1_router.include_router(router=routers.upgrade_router)
api_v1_router.include_router(router=routers.village_router)

# HTTP routers
api_v1_router.include_router(router=routers.auth_router)
api_v1_router.include_router(router=routers.group_router)
api_v1_router.include_router(router=routers.perm_router)
api_v1_router.include_router(router=routers.user_router)
api_v1_router.include_router(router=routers.ixc_user_router)

# WebSockets routers
api_v1_router.include_router(router=websockets.log_ws_router)
api_v1_router.include_router(router=websockets.metric_ws_router)
api_v1_router.include_router(router=websockets.user_ws_router)
