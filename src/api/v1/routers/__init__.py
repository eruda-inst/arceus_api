from .authentication_router import authentication_router
from .cobranca_router import cobranca_router
from .comercial_router import comercial_router
from .financeiro_router import financeiro_router
from .group_router import group_router
from .ixc_user_router import ixc_user_router
from .perm_router import perm_router
from .suporte_router import suporte_router
from .triagem_router import triagem_router
from .upgrade_router import upgrade_router
from .user_router import user_router
from .vila_router import vila_router

__all__ = [
    "authentication_router",
    "cobranca_router",
    "comercial_router",
    "financeiro_router",
    "group_router",
    "ixc_user_router",
    "perm_router",
    "suporte_router",
    "triagem_router",
    "upgrade_router",
    "user_router",
    "vila_router",
]
