from enum import StrEnum


class SuStatusCod(StrEnum):
    NOVO = "N"
    PENDENTE = "P"
    EM_PROGRESSO = "EP"
    SOLUCIONADO = "S"
    CANCELADO = "C"
