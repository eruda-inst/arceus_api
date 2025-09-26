from typing import List
from ..misc import Links, Meta
from pydantic import BaseModel, Field, PositiveInt
from app.api.v1.utils import StatusContratoRot


class Contrato(BaseModel):
    id: PositiveInt = Field(description="ID único do contrato.")
    id_login: PositiveInt = Field(description="ID de login associado ao contrato.")
    id_cliente: PositiveInt = Field(description="ID do cliente associado ao contrato.")
    status: StatusContratoRot = Field(description="Status atual do contrato.")
    contrato: str = Field(max_length=100, description="Número do contrato.")
    valor: float = Field(description="Valor do contrato.")
    data_vencimento: str = Field(description="Data de vencimento do contrato.")
    mac_onu: str = Field(description="MAC Address da ONU.")


class ContratoListOut(BaseModel):
    data: List[Contrato] = Field(description="Lista de contratos")
    meta: Meta
    links: Links
