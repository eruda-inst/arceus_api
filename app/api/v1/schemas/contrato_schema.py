from . import misc_schema
from app.api.v1 import utils
from pydantic import BaseModel, Field, PositiveInt, field_serializer


class StatusAcessoOut(BaseModel):
    status_acesso: utils.StatusInternetCod = Field(
        description="Status de acesso.", examples=[utils.StatusInternetRot.ATIVO]
    )

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


class Contrato(BaseModel):
    id: PositiveInt = Field(description="ID único do contrato.", examples=[123])
    id_login: PositiveInt = Field(
        description="ID de login associado ao contrato.", examples=[456]
    )
    id_cliente: PositiveInt = Field(
        description="ID do cliente associado ao contrato.", examples=[789]
    )
    nome_cliente: str = Field(
        description="Nome do cliente.", examples=["Nome do Cliente"]
    )
    status: utils.StatusContratoCod = Field(
        description="Status atual do contrato.",
        examples=[utils.StatusContratoRot.PRE_CONTRATO],
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

    @field_serializer("status")
    def serialize_status(self, v: utils.StatusContratoCod) -> utils.StatusContratoRot:
        cod = utils.StatusContratoCod
        rot = utils.StatusContratoRot

        mapping = {
            cod.PRE_CONTRATO: rot.PRE_CONTRATO,
            cod.ATIVO: rot.ATIVO,
            cod.INATIVO: rot.INATIVO,
            cod.NEGATIVADO: rot.NEGATIVADO,
            cod.DESISTIU: rot.DESISTIU,
        }

        return mapping[v]


class ContratoListOut(BaseModel):
    data: list[Contrato]
    meta: misc_schema.Meta


class ComercialContrato(BaseModel):
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


class ComercialContratoListOut(BaseModel):
    data: list[ComercialContrato]
    meta: misc_schema.Meta


class VilaContratoOut(BaseModel):
    id: PositiveInt = Field(description="ID do contrato.", examples=[1])
    id_login: PositiveInt = Field(description="ID do login do contrato.", examples=[12])
    id_cliente: PositiveInt = Field(description="ID do cliente.", examples=[123])
