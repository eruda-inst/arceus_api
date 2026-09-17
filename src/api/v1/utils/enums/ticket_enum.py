from enum import StrEnum


class SupportStatusCode(StrEnum):
    NEW = "N"
    PENDING = "P"
    IN_PROGRESS = "EP"
    SOLVED = "S"
    CANCELED = "C"


class SupportStatusLabel(StrEnum):
    NEW = "Novo"
    PENDING = "Pendente"
    IN_PROGRESS = "Em progresso"
    SOLVED = "Solucionado"
    CANCELED = "Cancelado"


class AddressOriginCode(StrEnum):
    CUSTOMER = "C"
    LOGIN = "L"
    CONTRACT = "CC"
    MANUAL = "M"


class TicketTypeCode(StrEnum):
    CUSTOMER = "C"
    OWN_STRUCTURE = "E"


class PriorityCode(StrEnum):
    LOW = "B"
    NORMAL = "M"
    HIGH = "A"
    CRITICAL = "C"
