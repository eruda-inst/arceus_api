from enum import Enum
from .. import maps, enums
from typing import TypeVar, Dict

K = TypeVar("K", bound=Enum)
V = TypeVar("V", bound=Enum)


def get_label(code: K, mapping: Dict[K, V]) -> V:
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
    status_atendimento_codigo: enums.SuStatusCod,
) -> enums.SuStatusRot:
    return get_label(status_atendimento_codigo, maps.STATUS_ATENDIMENTO)


def rotular_status_acesso(
    status_acesso_codigo: enums.StatusAcessoCod,
) -> enums.StatusAcessoRot:
    return get_label(status_acesso_codigo, maps.STATUS_ACESSO)


def rotular_status_onu(sinal_rx: float) -> enums.StatusONURot:
    if sinal_rx >= -15:
        return enums.StatusONURot.SATURADO
    elif sinal_rx >= -21:
        return enums.StatusONURot.EXCELENTE
    elif sinal_rx >= -26:
        return enums.StatusONURot.BOM
    elif sinal_rx >= -29:
        return enums.StatusONURot.REGULAR
    elif sinal_rx >= -31:
        return enums.StatusONURot.RUIM
    else:
        return enums.StatusONURot.PESSIMO
