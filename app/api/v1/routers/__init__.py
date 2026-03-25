from .suporte import suporte_router
from .comercial import comercial_router
from .financeiro import financeiro_router
from .triagem import triagem_router
from .cobranca import cobranca_router

__all__ = [
    "suporte_router",
    "comercial_router",
    "financeiro_router",
    "triagem_router",
    "cobranca_router",
]
