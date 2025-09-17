from enum import Enum


class SuStatusCod(str, Enum):
    NOVO = "N"
    PENDENTE = "P"
    EM_PROGRESSO = "EP"
    SOLUCIONADO = "S"
    CANCELADO = "C"