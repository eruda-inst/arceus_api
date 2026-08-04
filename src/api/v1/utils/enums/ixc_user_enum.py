from enum import StrEnum


class IXCUserStatusCod(StrEnum):
    ATIVO = "A"
    INATIVO = "I"


class IXCUserStatusLabel(StrEnum):
    ATIVO = "Ativo"
    INATIVO = "Inativo"


class IXCUserAccessTypeCod(StrEnum):
    AMBOS = "A"
    WEB = "W"
    MOBILE = "M"


class IXCUserAccessTypeLabel(StrEnum):
    AMBOS = "Ambos"
    WEB = "Web"
    MOBILE = "Mobile"
