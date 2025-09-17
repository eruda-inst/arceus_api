from enum import Enum


class StatusContratoRot(str, Enum):
    PRE_CONTRATO = "Pré-contrato"
    ATIVO = "Ativo"
    INATIVO = "Inativo"
    NEGATIVADO = "Negativo"
    DESISTIU = "Desistiu"