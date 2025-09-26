from typing import List
from pydantic import BaseModel, Field, PositiveInt, NonNegativeInt
from ..misc import Meta, Links


class FaturaAberta(BaseModel):
    id: PositiveInt = Field(description="ID da fatura.")
    id_contrato: NonNegativeInt = Field(description="ID de contrato associado à fatura")
    data_vencimento: str = Field(
        max_length=10, description="Data de vencimento da fatura."
    )
    preco: float = Field(description="Preço da fatura.")
    contrato: str = Field(description="Nome do contrato associado à fatura.")


class FaturaAbertaListOut(BaseModel):
    data: List[FaturaAberta]
    meta: Meta
    links: Links
