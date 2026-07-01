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


class AtivoRot(StrEnum):
    SIM = "Sim"
    NAO = "Não"


class TipoPessoaRot(StrEnum):
    FISICA = "Física"
    JURIDICA = "Jurídica"
    ESTRANGEIRO = "Estrangeiro"


class PrincipalRot(StrEnum):
    SIM = "Sim"
    NAO = "Não"


class LeadRot(StrEnum):
    SIM = "Sim"
    NAO = "Não"
