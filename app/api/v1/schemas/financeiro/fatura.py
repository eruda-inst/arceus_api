from typing import List
from pydantic import BaseModel, Field
from ..misc import Meta, Links


class Fatura(BaseModel):
    id: int = Field(ge=1, description="")
    id_contrato: int = Field(ge=0, description="")
    data_vencimento: str = Field(max_length=10, description="")
    preco: float = Field(ge=0, description="")
    contrato: str = Field(description="")


class FaturaOut(BaseModel):
    data: List[Fatura]
    meta: Meta
    links: Links
