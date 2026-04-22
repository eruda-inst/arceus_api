from enum import StrEnum


class AtivoCod(StrEnum):
    SIM = "S"
    NAO = "N"


class TipoPessoaCod(StrEnum):
    FISICA = "F"
    JURIDICA = "J"
    ESTRANGEIRO = "E"


class PrincipalCod(StrEnum):
    SIM = "S"
    NAO = "N"


class LeadCod(StrEnum):
    SIM = "S"
    NAO = "N"
