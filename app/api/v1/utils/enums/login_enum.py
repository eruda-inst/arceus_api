from enum import StrEnum


class StatusConexaoRot(StrEnum):
    CONECTADO = "Conectado"
    SEM_STATUS = "Sem status"
    DESCONECTADO = "Desconectado"


class StatusConexaoCod(StrEnum):
    CONECTADO = "S"
    SEM_STATUS = "SS"
    DESCONECTADO = "N"
