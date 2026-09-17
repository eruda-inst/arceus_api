"""
Enumerations for support tickets (status, address origin, type, priority).
"""

from enum import StrEnum


class SupportStatusCode(StrEnum):
    """
    Status codes for support tickets.
    """

    NEW = "N"
    PENDING = "P"
    IN_PROGRESS = "EP"
    SOLVED = "S"
    CANCELED = "C"


class SupportStatusLabel(StrEnum):
    """
    Human-readable labels for support ticket statuses.
    """

    NEW = "Novo"
    PENDING = "Pendente"
    IN_PROGRESS = "Em progresso"
    SOLVED = "Solucionado"
    CANCELED = "Cancelado"


class AddressOriginCode(StrEnum):
    """
    Codes for address origin in tickets.
    """

    CUSTOMER = "C"
    LOGIN = "L"
    CONTRACT = "CC"
    MANUAL = "M"


class TicketTypeCode(StrEnum):
    """
    Codes for ticket types.
    """

    CUSTOMER = "C"
    OWN_STRUCTURE = "E"


class PriorityCode(StrEnum):
    """
    Codes for ticket priorities.
    """

    LOW = "B"
    NORMAL = "M"
    HIGH = "A"
    CRITICAL = "C"
