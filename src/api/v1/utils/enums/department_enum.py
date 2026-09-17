"""
Enumerations for departments (sectors).
"""

from enum import StrEnum


class Department(StrEnum):
    """
    Department names in Portuguese.
    """

    SUPPORT = "Suporte"
    SALES = "Comercial"
    FINANCE = "Financeiro"
    TRIAGE = "Triagem"
    BILLING = "Cobrança"
