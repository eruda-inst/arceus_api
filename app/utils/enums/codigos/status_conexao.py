from enum import Enum


class StatusConexaoCod(str, Enum):
    CONECTADO = "S"
    SEM_STATUS = "SS"
    DESCONECTADO = "N"