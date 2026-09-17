from enum import StrEnum


class ConnectionStatusCode(StrEnum):
    CONNECTED = "S"
    NO_STATUS = "SS"
    DISCONNECTED = "N"


class ConnectionStatusLabel(StrEnum):
    CONNECTED = "Conectado"
    NO_STATUS = "Sem status"
    DISCONNECTED = "Desconectado"


class OnuStatusLabel(StrEnum):
    SATURATED = "Saturado"
    EXCELLENT = "Excelente"
    GOOD = "Bom"
    FAIR = "Regular"
    POOR = "Ruim"
    VERY_POOR = "Péssimo"
