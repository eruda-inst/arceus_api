from enum import StrEnum


class StatusContratoCod(StrEnum):
    PRE_CONTRATO = "P"
    ATIVO = "A"
    INATIVO = "I"
    NEGATIVADO = "N"
    DESISTIU = "D"
