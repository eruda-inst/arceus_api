from enum import Enum


class StatusContratoCod(str, Enum):
    PRE_CONTRATO = "P"
    ATIVO = "A"
    INATIVO = "I"
    NEGATIVADO = "N"
    DESISTIU = "D"
