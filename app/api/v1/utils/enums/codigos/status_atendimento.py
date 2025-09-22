from enum import Enum


class StatusAtendimentoCod(str, Enum):
    NOVO = "N"
    PENDENTE = "P"
    EM_PROGRESSO = "EP"
    SOLUCIONADO = "S"
    CANCELADO = "C"
