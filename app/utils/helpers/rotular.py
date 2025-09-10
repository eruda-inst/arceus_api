from typing import Literal, Dict


StatusConexaoCodigo = Literal["S", "SS", "N"]
StatusConexaoRotulo = Literal["Conectado", "Sem status", "Desconectado"]


def rotular_status_conexao(
    status_conexao_codigo: StatusConexaoCodigo
) -> StatusConexaoRotulo:
    status_conexao_mapa: Dict[StatusConexaoCodigo, StatusConexaoRotulo] = {
        "S": "Conectado",
        "SS": "Sem status",
        "N": "Desconectado"
    }
    return status_conexao_mapa[status_conexao_codigo]