from enum import StrEnum


class StatusAcessoRot(StrEnum):
    ATIVO = "Ativo"
    DESATIVADO = "Desativado"
    BLOQUEIO_MANUAL = "Bloqueio Manual"
    BLOQUEIO_AUTOMATICO = "Bloqueio Automático"
    FINANCEIRO_EM_ATRASO = "Financeiro em atraso"
    AGUARDANDO_ASSINATURA = "Aguardando Assinatura"
