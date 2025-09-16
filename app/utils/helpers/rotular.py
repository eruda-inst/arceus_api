from enum import Enum
from typing import Union
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

def rotular_status_onu(
    sinal_rx: float,
) -> str:
    '''
    📊 Legenda de Qualidade do Sinal ONU (em dBm)
    Faixa de Sinal (dBm)	Classificação
    -10 a -14	Saturado (potência excessiva)
    -15 a -20	Excelente (ótimo)
    -21 a -25	Bom
    -26 a -28	Regular / Aceitável
    -29 a -30	Ruim (fraco, instável)
    ≤ -31	Péssimo (quase sem conexão)
    '''
    if sinal_rx >= -15:
        return "Saturado"
    elif sinal_rx >= -21:
        return "Excelente"
    elif sinal_rx >= -26:
        return "Bom"
    elif sinal_rx >= -29:
        return "Regular"
    elif sinal_rx >= -31:
        return "Ruim"
    else:
        return "Péssimo"