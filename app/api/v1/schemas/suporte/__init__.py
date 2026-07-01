from .onu_suporte_schema import StatusONU, StatusONUOut
from .conexao_suporte_schema import StatusConexao, StatusConexaoOut
from .atendimento_suporte_schema import (
    Atendimento,
    AtendimentoIn,
    AtendimentoOut,
    AtendimentoCreate,
)

__all__ = [
    "StatusONU",
    "StatusONUOut",
    "StatusConexao",
    "StatusConexaoOut",
    "Atendimento",
    "AtendimentoIn",
    "AtendimentoOut",
    "AtendimentoCreate",
]
