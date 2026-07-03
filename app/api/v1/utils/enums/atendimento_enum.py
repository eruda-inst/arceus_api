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


class OrigemEnderecoCod(StrEnum):
    CLIENTE = "C"
    LOGIN = "L"
    CONTRATO = "CC"
    MANUAL = "M"


class TipoAtendimentoCod(StrEnum):
    CLIENTE = "C"
    ESTRUTURA_PROPRIA = "E"


class PrioridadeCod(StrEnum):
    BAIXA = "B"
    NORMAL = "M"
    ALTA = "A"
    CRITICA = "C"
