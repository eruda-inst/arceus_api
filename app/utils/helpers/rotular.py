from typing import Literal, Dict


StatusConexaoCodigo = Literal["S", "SS", "N"]
StatusConexaoRotulo = Literal["Conectado", "Sem status", "Desconectado"]

StatusContratoCodigo = Literal["P", "A", "I", "N", "D"]
StatusContratoRotulo = Literal["Pré-contrato", "Ativo", "Inativo", "Negativado", "Desistiu"]

StatusAtendimentoCodigo = Literal["N", "P", "EP", "S", "C"]
StatusAtendimentoRotulo = Literal["Novo", "Pendente", "Em progresso", "Solucionado", "Cancelado"]


def rotular_status_conexao(
    status_conexao_codigo: StatusConexaoCodigo
) -> StatusConexaoRotulo:
    status_conexao_mapa: Dict[StatusConexaoCodigo, StatusConexaoRotulo] = {
        "S": "Conectado",
        "SS": "Sem status",
        "N": "Desconectado"
    }
    return status_conexao_mapa[status_conexao_codigo]


def rotular_status_contrato(
    status_contrato_codigo: StatusContratoCodigo
) -> StatusContratoRotulo:
    status_contrato_mapa: Dict[StatusContratoCodigo, StatusContratoRotulo] = {
        "P": "Pré-contrato",
        "A": "Ativo",
        "I": "Inativo",
        "N": "Negativado",
        "D": "Desistiu"
    }
    return status_contrato_mapa[status_contrato_codigo]


def rotular_status_atendimento(
    status_contrato_codigo: StatusAtendimentoCodigo
):
    status_contrato_mapa: Dict[StatusAtendimentoCodigo, StatusAtendimentoRotulo] = {
        "N": "Novo",
        "P": "Pendente",
        "EP": "Em progresso",
        "S": "Solucionado",
        "C": "Cancelado",
    }
    return status_contrato_mapa[status_contrato_codigo]