from enum import Enum
from typing import Union
from .. import maps, enums


def get_label(
    code: Enum, mapping: dict
) -> Union[enums.StatusConexaoRot, enums.StatusContratoRot, enums.StatusAtendimentoRot]:
    """Obtém um rótulo de um mapeamento com base em um código.

    Args:
        code (Enum): O código a ser pesquisado.
        mapping (dict): O mapeamento para pesquisar.

    Returns:
        Union[enums.StatusConexaoRot, enums.StatusContratoRot, enums.StatusAtendimentoRot]:
            O rótulo correspondente ao código.
    """
    return mapping[code]


def rotular_status_conexao(
    status_conexao_codigo: enums.StatusConexaoCod,
) -> enums.StatusConexaoRot:
    """Rotula o status da conexão com base no código.

    Args:
        status_conexao_codigo (enums.StatusConexaoCod): O código do status da conexão.

    Returns:
        enums.StatusConexaoRot: O rótulo do status da conexão.
    """
    return get_label(status_conexao_codigo, maps.STATUS_CONEXAO)


def rotular_status_contrato(
    status_contrato_codigo: enums.StatusContratoCod,
) -> enums.StatusContratoRot:
    """Rotula o status do contrato com base no código.

    Args:
        status_contrato_codigo (enums.StatusContratoCod): O código do status do contrato.

    Returns:
        enums.StatusContratoRot: O rótulo do status do contrato.
    """
    return get_label(status_contrato_codigo, maps.STATUS_CONTRATO)


def rotular_status_atendimento(
    status_atendimento_codigo: enums.StatusAtendimentoCod,
) -> enums.StatusAtendimentoRot:
    """Rotula o status do atendimento com base no código.

    Args:
        status_atendimento_codigo (enums.StatusAtendimentoCod): O código do status do atendimento.

    Returns:
        enums.StatusAtendimentoRot: O rótulo do status do atendimento.
    """
    return get_label(status_atendimento_codigo, maps.STATUS_ATENDIMENTO)


def rotular_status_acesso(
    status_acesso_codigo: enums.StatusAcessoCod,
) -> enums.StatusAcessoRot:
    """Rotula o status de acesso com base no código.

    Args:
        status_acesso_codigo (enums.StatusAcessoCod): O código do status de acesso.

    Returns:
        enums.StatusAcessoRot: O rótulo do status de acesso.
    """
    return get_label(status_acesso_codigo, maps.STATUS_ACESSO)


def rotular_status_onu(sinal_rx: float) -> str:
    """Rotula o status da ONU com base no sinal RX.

    Args:
        sinal_rx (float): O sinal RX da ONU.

    Returns:
        str: O rótulo do status da ONU.
    """
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
