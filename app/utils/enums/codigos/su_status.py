from enum import Enum


class SuStatusCod(Enum):
    NOVO = "N",
    PENDENTE = "P",
    EM_PROGRESSO = "EP",
    SOLUCIONADO = "S",
    CANCELADO = "C"