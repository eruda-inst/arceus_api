"""
Enumerations for connection status and ONU status.
"""

from enum import StrEnum


class ConnectionStatusCode(StrEnum):
    """
    Codes for connection status.
    """

    CONNECTED = "S"
    NO_STATUS = "SS"
    DISCONNECTED = "N"


class ConnectionStatusLabel(StrEnum):
    """
    Human-readable labels for connection status.
    """

    CONNECTED = "Conectado"
    NO_STATUS = "Sem status"
    DISCONNECTED = "Desconectado"


class OnuStatusLabel(StrEnum):
    """
    Human-readable labels for ONU signal quality.
    """

    SATURATED = "Saturado"
    EXCELLENT = "Excelente"
    GOOD = "Bom"
    FAIR = "Regular"
    POOR = "Ruim"
    VERY_POOR = "Péssimo"
