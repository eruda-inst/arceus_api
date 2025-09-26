from typing import List
from ..misc import Links, Meta
from pydantic import BaseModel, Field, PositiveInt
from app.api.v1.utils import StatusAcessoRot


class Contrato(BaseModel):
    id: PositiveInt = Field(description="ID único do contrato.")
    contrato: str = Field(max_length=100, description="Número do contrato.")
    valor: float = Field(description="Valor do contrato.")
    status_acesso: StatusAcessoRot = Field(description="Status do acesso do contrato.")
    data_vencimento: str = Field(description="Data de vencimento do contrato.")


class ContratoListOut(BaseModel):
    data: List[Contrato] = Field(description="Lista de contratos")
    meta: Meta
    links: Links
