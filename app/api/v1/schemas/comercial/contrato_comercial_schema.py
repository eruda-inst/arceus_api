from typing import List
from .. import misc_schema
from app.api.v1 import utils
from pydantic import BaseModel, Field, PositiveInt, field_serializer


class Contrato(BaseModel):
    id: PositiveInt = Field(description="ID único do contrato.", examples=[1234])
    contrato: str = Field(
        max_length=100,
        description="Número do contrato.",
        examples=["NEWNET PADRAO - 250MB - 06/2025"],
    )
    nome_cliente: str = Field(
        description="Nome do cliente.", examples=["Nome do Cliente"]
    )
    valor: float = Field(description="Valor do contrato.", examples=[99.99])
    status_acesso: utils.StatusInternetCod = Field(
        description="Status do acesso do contrato.",
        examples=[utils.StatusInternetRot.ATIVO],
    )
    data_vencimento: str = Field(
        description="Data de vencimento do contrato.", examples=["2025-12-31"]
    )
    id_cliente: PositiveInt = Field(description="ID do cliente.", examples=[12345])
    id_login: PositiveInt = Field(description="ID de login.", examples=[123456])

    @field_serializer("status_acesso")
    def serialize_status(self, v: utils.StatusInternetCod) -> utils.StatusInternetRot:
        cod = utils.StatusInternetCod
        rot = utils.StatusInternetRot

        mapping = {
            cod.ATIVO: rot.ATIVO,
            cod.DESATIVADO: rot.DESATIVADO,
            cod.BLOQUEIO_MANUAL: rot.BLOQUEIO_MANUAL,
            cod.BLOQUEIO_AUTOMATICO: rot.BLOQUEIO_AUTOMATICO,
            cod.FINANCEIRO_EM_ATRASO: rot.FINANCEIRO_EM_ATRASO,
            cod.AGUARDANDO_ASSINATURA: rot.AGUARDANDO_ASSINATURA,
        }

        return mapping[v]


class ContratoListOut(BaseModel):
    data: List[Contrato] = Field(description="Lista de contratos")
    meta: misc_schema.Meta
