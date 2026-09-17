from enum import StrEnum


class IXCUserStatusCode(StrEnum):
    ACTIVE = "A"
    INACTIVE = "I"


class IXCUserStatusLabel(StrEnum):
    ACTIVE = "Ativo"
    INACTIVE = "Inativo"


class IXCUserAccessTypeCode(StrEnum):
    BOTH = "A"
    WEB = "W"
    MOBILE = "M"


class IXCUserAccessTypeLabel(StrEnum):
    BOTH = "Ambos"
    WEB = "Web"
    MOBILE = "Mobile"
