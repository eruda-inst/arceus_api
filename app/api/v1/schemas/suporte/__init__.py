from .onu import StatusONU, StatusONUOut
from .contrato import (
    Contrato as SuporteContrato,
    ContratoListOut as SuporteContratoListOut,
)
from .conexao import StatusConexao, StatusConexaoOut
from .atendimento import Atendimento, AtendimentoIn, AtendimentoOut, AtendimentoCreate
from .ip import IPUpdate

__all__ = [
    "SuporteContrato",
    "SuporteContratoListOut",
    "StatusONU",
    "StatusONUOut",
    "StatusConexao",
    "StatusConexaoOut",
    "Atendimento",
    "AtendimentoIn",
    "AtendimentoOut",
    "AtendimentoCreate",
    "IPUpdate",
]
