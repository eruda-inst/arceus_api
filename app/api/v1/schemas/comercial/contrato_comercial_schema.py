from .. import misc_schema
from typing import List
from app.api.v1 import utils
from pydantic import BaseModel, Field, PositiveInt


class Contrato(BaseModel):
    id: PositiveInt = Field(description="ID único do contrato.", examples=[1234])
    contrato: str = Field(
        max_length=100,
        description="Número do contrato.",
        examples=["NEWNET PADRAO - 250MB - 06/2025"],
    )
    valor: float = Field(description="Valor do contrato.", examples=[99.99])
    status_acesso: utils.StatusAcessoRot = Field(
        description="Status do acesso do contrato.",
        examples=[utils.StatusAcessoRot.ATIVO],
    )
    data_vencimento: str = Field(
        description="Data de vencimento do contrato.", examples=["2025-12-31"]
    )
    id_cliente: PositiveInt = Field(description="ID do cliente.", examples=[12345])
    id_login: PositiveInt = Field(description="ID de login.", examples=[123456])


class ContratoListOut(BaseModel):
    data: List[Contrato] = Field(description="Lista de contratos")
    meta: misc_schema.Meta
