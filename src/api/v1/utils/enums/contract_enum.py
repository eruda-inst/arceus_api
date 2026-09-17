from enum import StrEnum


class ContractStatusCode(StrEnum):
    PRE_CONTRACT = "P"
    ACTIVE = "A"
    INACTIVE = "I"
    NEGATIVE = "N"
    WITHDREW = "D"


class ContractStatusLabel(StrEnum):
    PRE_CONTRACT = "Pré-contrato"
    ACTIVE = "Ativo"
    INACTIVE = "Inativo"
    NEGATIVE = "Negativo"
    WITHDREW = "Desistiu"


class InternetStatusLabel(StrEnum):
    ACTIVE = "Ativo"
    DEACTIVATED = "Desativado"
    MANUAL_BLOCK = "Bloqueio Manual"
    AUTOMATIC_BLOCK = "Bloqueio Automático"
    FINANCIAL_OVERDUE = "Financeiro em atraso"
    AWAITING_SIGNATURE = "Aguardando Assinatura"


class InternetStatusCode(StrEnum):
    ACTIVE = "A"
    DEACTIVATED = "D"
    MANUAL_BLOCK = "CM"
    AUTOMATIC_BLOCK = "CA"
    FINANCIAL_OVERDUE = "FA"
    AWAITING_SIGNATURE = "AA"
