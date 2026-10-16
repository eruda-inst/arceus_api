"""
Enumerations for person types (lead).
"""

from enum import StrEnum


class PersonTypeCode(StrEnum):
    """
    Codes for person types.
    """

    INDIVIDUAL = "F"
    LEGAL_ENTITY = "J"
    FOREIGN = "E"


class PersonTypeLabel(StrEnum):
    """
    Human-readable labels for person types.
    """

    INDIVIDUAL = "Física"
    LEGAL_ENTITY = "Jurídica"
    FOREIGN = "Estrangeiro"
