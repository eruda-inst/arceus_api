from enum import Enum


class StatusAtendimentoRot(str, Enum):
    NOVO = "Novo"
    PENDENTE = "Pendente"
    EM_PROGRESSO = "Em progresso"
    SOLUCIONADO = "Solucionado"
    CANCELADO = "Cancelado"