from .. import misc_schema
from typing import List
from pydantic import BaseModel, Field, PositiveInt, NonNegativeInt, PositiveFloat


class Fatura(BaseModel):
    id: PositiveInt = Field(description="ID da fatura.", examples=[123])
    data_vencimento: str = Field(
        max_length=10,
        description="Data de vencimento da fatura.",
        examples=["2025-12-31"],
    )
    preco: float = Field(description="Preço da fatura.", examples=[99.99])


class FaturaAberta(Fatura):
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


class LinhaDigitavelBase(BaseModel):
    linha_digitavel: str = Field(
        min_length=47,
        max_length=47,
        description="Linha digitável.",
        examples=["12345678901234567890123456789012345678901234567"],
    )


class LinhaDigitavelOut(BaseModel):
    data: LinhaDigitavelBase = Field()


class FaturaPagaBase(Fatura):
    valor_pago: PositiveFloat = Field(description="Valor pago.", examples=[99.99])
    data_pagamento: str = Field(
        max_length=10,
        description="Data de pagamento da fatura.",
        examples=["2025-12-31"],
    )
