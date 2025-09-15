from typing import List
from .misc import Links, Meta
from pydantic import BaseModel, Field
from ..utils import StatusContratoRotulo


class StatusContrato(BaseModel):
    status_contrato: StatusContratoRotulo = Field(description="Status atual do contrato.")

class StatusContratoOut(BaseModel):
    data: StatusContrato

class Contrato(BaseModel):
    id: int = Field(description="ID único do contrato.")
    id_login: int = Field(description="ID de login associado ao contrato.")
    status: StatusContratoRotulo = Field(description="Status atual do contrato.")
    contrato: str = Field(max_length=100, description="Número do contrato.")
    valor: float = Field(description="Valor do contrato.")
    data_vencimento: str = Field(description="Data de vencimento do contrato.")

class ContratoListOut(BaseModel):
    data: List[Contrato] = Field(default=None, description="Lista de contratos")
    meta: Meta
    links: Links