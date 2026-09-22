"""
API v1 router aggregator.

Mounts all HTTP routers and WebSocket routers under the `/api/v1` prefix.
"""

from fastapi import APIRouter, Depends

from . import deps, routers, ws

# Dependency aliases
CredsDep = Depends(deps.get_creds)
CurrUserDep = Depends(deps.get_curr_user)
CurrUserWsDep = Depends(deps.get_curr_user_ws)


# Main API v1 router with the versioned prefix
api_v1_router = APIRouter(prefix="/api/v1")

# HTTP department routers
api_v1_router.include_router(router=routers.billing_router, dependencies=[CredsDep])
api_v1_router.include_router(router=routers.sales_router, dependencies=[CredsDep])
api_v1_router.include_router(router=routers.finance_router, dependencies=[CredsDep])
api_v1_router.include_router(router=routers.support_router, dependencies=[CredsDep])
api_v1_router.include_router(router=routers.triage_router, dependencies=[CredsDep])
api_v1_router.include_router(router=routers.upgrade_router, dependencies=[CredsDep])
api_v1_router.include_router(router=routers.village_router, dependencies=[CredsDep])

# HTTP routers
api_v1_router.include_router(router=routers.auth_router)
api_v1_router.include_router(router=routers.group_router, dependencies=[CurrUserDep])
api_v1_router.include_router(router=routers.perm_router)
api_v1_router.include_router(router=routers.user_router, dependencies=[CurrUserDep])
api_v1_router.include_router(router=routers.ixc_user_router, dependencies=[CurrUserDep])

# WebSockets routers
api_v1_router.include_router(router=ws.log_ws_router, dependencies=[CurrUserWsDep])
api_v1_router.include_router(router=ws.metric_ws_router, dependencies=[CurrUserWsDep])
api_v1_router.include_router(router=ws.user_ws_router, dependencies=[CurrUserWsDep])
