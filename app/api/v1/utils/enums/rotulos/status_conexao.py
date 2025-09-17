from enum import Enum


class StatusConexaoRot(str, Enum):
    CONECTADO = "Conectado"
    SEM_STATUS = "Sem status"
    DESCONECTADO = "Desconectado"