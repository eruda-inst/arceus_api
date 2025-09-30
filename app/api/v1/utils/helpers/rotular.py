from .. import maps
from .. import enums
from enum import Enum
from typing import Union


def get_label(
    code: Enum, mapping: dict
) -> Union[enums.StatusConexaoRot, enums.StatusContratoRot, enums.StatusAtendimentoRot]:
    return mapping[code]


def rotular_status_conexao(
    status_conexao_codigo: enums.StatusConexaoCod,
) -> enums.StatusConexaoRot:
    return get_label(status_conexao_codigo, maps.STATUS_CONEXAO)


def rotular_status_contrato(
    status_contrato_codigo: enums.StatusContratoCod,
) -> enums.StatusContratoRot:
    return get_label(status_contrato_codigo, maps.STATUS_CONTRATO)


def rotular_status_atendimento(
    status_atendimento_codigo: enums.StatusAtendimentoCod,
) -> enums.StatusAtendimentoRot:
    return get_label(status_atendimento_codigo, maps.STATUS_ATENDIMENTO)


def rotular_status_acesso(
    status_acesso_codigo: enums.StatusAcessoCod,
) -> enums.StatusAcessoRot:
    return get_label(status_acesso_codigo, maps.STATUS_ACESSO)


def rotular_status_onu(sinal_rx: float) -> str:
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
