from enum import StrEnum


class TipoPessoaCod(StrEnum):
    FISICA = "F"
    JURIDICA = "J"
    ESTRANGEIRO = "E"


class TipoPessoaRot(StrEnum):
    FISICA = "Física"
    JURIDICA = "Jurídica"
    ESTRANGEIRO = "Estrangeiro"
