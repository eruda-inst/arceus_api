from enum import Enum


class StatusAcessoCod(str, Enum):
    ATIVO = "A"
    DESATIVADO = "D"
    BLOQUEIO_MANUAL = "CM"
    BLOQUEIO_AUTOMATICO = "CA"
    FINANCEIRO_EM_ATRASO = "FA"
    AGUARDANDO_ASSINATURA = "AA"
