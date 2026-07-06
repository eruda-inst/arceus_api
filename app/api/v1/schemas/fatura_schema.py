from . import Meta
from pydantic import BaseModel, Field, PositiveInt, NonNegativeInt


class LinhaDigitavelOut(BaseModel):
    linha_digitavel: str = Field(
        min_length=47,
        max_length=47,
        description="Linha digitável.",
        examples=["123..."],
    )


class FaturaAberta(BaseModel):
    id: PositiveInt = Field(description="ID da fatura.", examples=[1])
    data_vencimento: str = Field(
        description="Data de vencimento da fatura.",
        # Não pode haver isto, pois o IXC é quebrado
        # min_length=10,  # YYYY-MM-AA
        # max_length=10,  # YYYY-MM-AA
        examples=["dd/mm/aaaa"],
    )
    preco: float = Field(ge=0, description="Preço da fatura.", examples=[12.34])
    id_contrato: NonNegativeInt = Field(description="ID do contrato", examples=[12])
    contrato: str = Field(description="Nome do plano.", examples=["Nome do plano"])


class FaturaAbertaListOut(BaseModel):
    data: list[FaturaAberta]
    meta: Meta
