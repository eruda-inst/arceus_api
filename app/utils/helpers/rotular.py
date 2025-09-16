from enum import Enum
from typing import Union, Any
from ..maps import STATUS_CONEXAO, STATUS_ATENDIMENTO, STATUS_CONTRATO
from ..enums import (
    StatusConexaoCod,
    StatusContratoCod,
    StatusAtendimentoCod,
    StatusConexaoRot,
    StatusContratoRot,
    StatusAtendimentoRot
)


def get_label(
    code: Enum,
    mapping: dict
) -> Union[StatusConexaoRot, StatusContratoRot, StatusAtendimentoRot]:
    return mapping[code]

def rotular_status_conexao(
    status_conexao_codigo: StatusConexaoCod,
) -> StatusConexaoRot:
    return get_label(status_conexao_codigo, STATUS_CONEXAO)

def rotular_status_contrato(
    status_contrato_codigo: StatusContratoCod,
) -> StatusContratoRot:
    return get_label(status_contrato_codigo, STATUS_CONTRATO)

def rotular_status_atendimento(
    status_atendimento_codigo: StatusAtendimentoCod,
) -> StatusAtendimentoRot:
    return get_label(status_atendimento_codigo, STATUS_ATENDIMENTO)