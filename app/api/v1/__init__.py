from .clients import IXCClient, OpaClient
from .core import settings, Settings
from .routers import suporte_router, comercial_router
from .schemas import (
    Atendimento,
    AtendimentoCreate,
    AtendimentoIn,
    AtendimentoOut,
    Contrato,
    ContratoListOut,
    Links,
    Meta,
    StatusONU,
    StatusConexaoOut,
    StatusConexao,
    StatusONUOut

)
from .services import SuporteService, ComercialService
from .utils import (
    rotular_status_atendimento,
    rotular_status_conexao,
    rotular_status_contrato,
    rotular_status_acesso,
    rotular_status_onu,
    StatusAtendimentoCod,
    StatusContratoCod,
    OrigemEnderecoCod,
    StatusConexaoCod,
    PrioridadeCod,
    SuStatusCod,
    TipoCod,
    StatusAcessoCod,
    STATUS_ACESSO,
    StatusAcessoRot,
    StatusAtendimentoRot,
    StatusContratoRot,
    StatusConexaoRot,
    StatusONURot,
    STATUS_ATENDIMENTO,
    STATUS_CONEXAO,
    STATUS_CONTRATO,
    SortOrder
)