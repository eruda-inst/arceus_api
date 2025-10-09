from .. import misc
from typing import List
from pydantic import BaseModel, Field, PositiveInt, NonNegativeInt, PositiveFloat


class Fatura(BaseModel):
    id: PositiveInt = Field(description="ID da fatura.")
    data_vencimento: str = Field(
        max_length=10, description="Data de vencimento da fatura."
    )
    preco: float = Field(description="Preço da fatura.")


class FaturaAberta(Fatura):
    id_contrato: NonNegativeInt = Field(description="ID de contrato associado à fatura")
    contrato: str = Field(description="Nome do contrato associado à fatura.")


class FaturaAbertaListOut(BaseModel):
    data: List[FaturaAberta]
    meta: misc.Meta
    links: misc.Links


class LinhaDigitavelBase(BaseModel):
    linha_digitavel: str = Field(
        min_length=47, max_length=47, description="Linha digitável."
    )


class LinhaDigitavelOut(BaseModel):
    data: LinhaDigitavelBase


class FaturaPagaBase(Fatura):
    pagamento_valor: PositiveFloat = Field(description="Valor pago.")
    pagamento_data: str = Field(
        max_length=10, description="Data de pagamento da fatura."
    )
