"""
Enumerations for contract and internet status codes and labels.
"""

from enum import StrEnum


class ContractStatusCode(StrEnum):
    """
    Status codes for contracts in IXC.
    """

    PRE_CONTRACT = "P"
    ACTIVE = "A"
    INACTIVE = "I"
    NEGATIVE = "N"
    WITHDREW = "D"


class ContractStatusLabel(StrEnum):
    """
    Human-readable labels for contract status codes.
    """

    PRE_CONTRACT = "Pré-contrato"
    ACTIVE = "Ativo"
    INACTIVE = "Inativo"
    NEGATIVE = "Negativo"
    WITHDREW = "Desistiu"


class InternetStatusLabel(StrEnum):
    """
    Human-readable labels for internet access status.
    """

    ACTIVE = "Ativo"
    DEACTIVATED = "Desativado"
    MANUAL_BLOCK = "Bloqueio Manual"
    AUTOMATIC_BLOCK = "Bloqueio Automático"
    FINANCIAL_OVERDUE = "Financeiro em atraso"
    AWAITING_SIGNATURE = "Aguardando Assinatura"


class InternetStatusCode(StrEnum):
    """
    Status codes for internet access in IXC.
    """

    ACTIVE = "A"
    DEACTIVATED = "D"
    MANUAL_BLOCK = "CM"
    AUTOMATIC_BLOCK = "CA"
    FINANCIAL_OVERDUE = "FA"
    AWAITING_SIGNATURE = "AA"
