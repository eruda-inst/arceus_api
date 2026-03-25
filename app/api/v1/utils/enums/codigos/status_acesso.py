from enum import StrEnum


class StatusAcessoCod(StrEnum):
    ATIVO = "A"
    DESATIVADO = "D"
    BLOQUEIO_MANUAL = "CM"
    BLOQUEIO_AUTOMATICO = "CA"
    FINANCEIRO_EM_ATRASO = "FA"
    AGUARDANDO_ASSINATURA = "AA"
