"""
Miscellaneous enumerations for yes/no codes and labels.
"""

from enum import StrEnum


class YesNoCode(StrEnum):
    """
    Codes for yes/no values.
    """

    YES = "S"
    NO = "N"


class YesNoLabel(StrEnum):
    """
    Human-readable labels for yes/no values.
    """

    YES = "Sim"
    NO = "Não"
