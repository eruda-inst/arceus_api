from typing import List
from .. import misc_schema
from pydantic import BaseModel, Field, PositiveInt, NonNegativeInt


class LinhaDigitavelBase(BaseModel):
    linha_digitavel: str = Field(
        min_length=47,
        max_length=47,
        description="Linha digitável.",
        examples=["123..."],
    )


class LinhaDigitavelOut(BaseModel):
    data: LinhaDigitavelBase


class FaturaAberta(BaseModel):
    id: PositiveInt = Field(description="ID da fatura.", examples=[123])
    data_vencimento: str = Field(
        max_length=10,
        description="Data de vencimento da fatura.",
        examples=["2025-12-31"],
    )
    preco: float = Field(description="Preço da fatura.", examples=[99.99])
    id_contrato: NonNegativeInt = Field(
        description="ID de contrato associado à fatura", examples=[1234]
    )
    contrato: str = Field(
        description="Nome do contrato associado à fatura.",
        examples=["NEWNET PADRAO - 250MB - 06/2025"],
    )


class FaturaAbertaListOut(BaseModel):
    data: List[FaturaAberta]
    meta: misc_schema.Meta
