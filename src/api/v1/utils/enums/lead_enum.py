from enum import StrEnum


class PersonTypeCode(StrEnum):
    INDIVIDUAL = "F"
    LEGAL_ENTITY = "J"
    FOREIGN = "E"


class PersonTypeLabel(StrEnum):
    INDIVIDUAL = "Física"
    LEGAL_ENTITY = "Jurídica"
    FOREIGN = "Estrangeiro"
