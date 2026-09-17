"""
Enumerations for IXC user status and access types.
"""

from enum import StrEnum


class IXCUserStatusCode(StrEnum):
    """
    Status codes for IXC users.
    """

    ACTIVE = "A"
    INACTIVE = "I"


class IXCUserStatusLabel(StrEnum):
    """
    Human-readable labels for IXC user status.
    """

    ACTIVE = "Ativo"
    INACTIVE = "Inativo"


class IXCUserAccessTypeCode(StrEnum):
    """
    Access type codes for IXC users.
    """

    BOTH = "A"
    WEB = "W"
    MOBILE = "M"


class IXCUserAccessTypeLabel(StrEnum):
    """
    Human-readable labels for IXC user access types.
    """

    BOTH = "Ambos"
    WEB = "Web"
    MOBILE = "Mobile"
