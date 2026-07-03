from enum import StrEnum


class StatusConexaoRot(StrEnum):
    CONECTADO = "Conectado"
    SEM_STATUS = "Sem status"
    DESCONECTADO = "Desconectado"


class StatusConexaoCod(StrEnum):
    CONECTADO = "S"
    SEM_STATUS = "SS"
    DESCONECTADO = "N"


class StatusOnuRot(StrEnum):
    SATURADO = "Saturado"
    EXCELENTE = "Excelente"
    BOM = "Bom"
    REGULAR = "Regular"
    RUIM = "Ruim"
    PESSIMO = "Péssimo"
    SEM_ONU = "Sem ONU"
