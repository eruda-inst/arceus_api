from enum import StrEnum


class StatusContratoCod(StrEnum):
    PRE_CONTRATO = "P"
    ATIVO = "A"
    INATIVO = "I"
    NEGATIVADO = "N"
    DESISTIU = "D"


class StatusContratoRot(StrEnum):
    PRE_CONTRATO = "Pré-contrato"
    ATIVO = "Ativo"
    INATIVO = "Inativo"
    NEGATIVADO = "Negativo"
    DESISTIU = "Desistiu"


class StatusInternetRot(StrEnum):
    ATIVO = "Ativo"
    DESATIVADO = "Desativado"
    BLOQUEIO_MANUAL = "Bloqueio Manual"
    BLOQUEIO_AUTOMATICO = "Bloqueio Automático"
    FINANCEIRO_EM_ATRASO = "Financeiro em atraso"
    AGUARDANDO_ASSINATURA = "Aguardando Assinatura"


class StatusInternetCod(StrEnum):
    ATIVO = "A"
    DESATIVADO = "D"
    BLOQUEIO_MANUAL = "CM"
    BLOQUEIO_AUTOMATICO = "CA"
    FINANCEIRO_EM_ATRASO = "FA"
    AGUARDANDO_ASSINATURA = "AA"
