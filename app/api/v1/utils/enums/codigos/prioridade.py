from enum import Enum


class PrioridadeCod(str, Enum):
    BAIXA = "B"
    NORMAL = "M"
    ALTA = "A"
    CRITICA = "C"
