from enum import StrEnum


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
