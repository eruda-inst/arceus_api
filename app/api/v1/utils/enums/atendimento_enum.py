from enum import StrEnum


class SuStatusCod(StrEnum):
    NOVO = "N"
    PENDENTE = "P"
    EM_PROGRESSO = "EP"
    SOLUCIONADO = "S"
    CANCELADO = "C"


class SuStatusRot(StrEnum):
    NOVO = "Novo"
    PENDENTE = "Pendente"
    EM_PROGRESSO = "Em progresso"
    SOLUCIONADO = "Solucionado"
    CANCELADO = "Cancelado"
