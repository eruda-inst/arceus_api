from .auth_router import auth_router
from .billing_router import billing_router
from .finance_router import finance_router
from .group_router import group_router
from .ixc_user_router import ixc_user_router
from .perm_router import perm_router
from .sales_router import sales_router
from .support_router import support_router
from .triage_router import triage_router
from .upgrade_router import upgrade_router
from .user_router import user_router
from .village_router import village_router

__all__ = [
    "auth_router",
    "billing_router",
    "finance_router",
    "group_router",
    "ixc_user_router",
    "perm_router",
    "sales_router",
    "support_router",
    "triage_router",
    "upgrade_router",
    "user_router",
    "village_router",
]
