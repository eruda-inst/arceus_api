from enum import Enum


class StatusContratoCod(Enum):
    PRE_CONTRATO = "P"
    ATIVO = "A"
    INATIVO = "I"
    NEGATIVADO = "N"
    DESISTIU = "D"