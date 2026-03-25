from enum import StrEnum


class StatusAtendimentoRot(StrEnum):
    NOVO = "Novo"
    PENDENTE = "Pendente"
    EM_PROGRESSO = "Em progresso"
    SOLUCIONADO = "Solucionado"
    CANCELADO = "Cancelado"
