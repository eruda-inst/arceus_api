"""
Enumerations for permission names and codes.
"""

from enum import StrEnum


class PermNames(StrEnum):
    """
    Human-readable permission names.
    """

    READ_METRIC = "Ver métricas"
    READ_LOG = "Ver logs"
    CREATE_USER = "Criar usuários"
    READ_USER = "Ver usuários"
    UPDATE_USER = "Alterar usuários"
    DEL_USER = "Remover usuários"


class PermCodes(StrEnum):
    """
    Permission codes used for authorization checks.
    """

    READ_METRIC = "ver:metricas"
    READ_LOG = "ver:logs"
    CREATE_USER = "criar:usuarios"
    READ_USER = "ver:usuarios"
    UPDATE_USER = "alterar:usuarios"
    DEL_USER = "remover:usuarios"
