from typing import List
from .. import misc_schema
from app.api.v1 import utils
from pydantic import BaseModel, Field, PositiveInt


class Contrato(BaseModel):
    id: PositiveInt = Field(description="ID único do contrato.", examples=[123])
    id_login: PositiveInt = Field(
        description="ID de login associado ao contrato.", examples=[456]
    )
    id_cliente: PositiveInt = Field(
        description="ID do cliente associado ao contrato.", examples=[789]
    )
    status: utils.StatusContratoRot = Field(
        description="Status atual do contrato.",
        examples=[utils.enums.rotulos.StatusContratoRot.PRE_CONTRATO],
    )
    contrato: str = Field(
        max_length=100,
        description="Número do contrato.",
        examples=["NEWNET PADRAO - 250MB - 06/2025"],
    )
    valor: float = Field(description="Valor do contrato.", examples=[99.99])
    data_vencimento: str = Field(
        description="Data de vencimento do contrato.", examples=["2025-12-31"]
    )
    mac_onu: str = Field(description="MAC Address da ONU.", examples=["AB1230001234"])


class ContratoListOut(BaseModel):
    data: List[Contrato] = Field(
        description="Lista de contratos",
    )
    meta: misc_schema.Meta = Field()
