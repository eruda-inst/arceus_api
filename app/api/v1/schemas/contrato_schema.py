from . import Meta
from .. import utils
from pydantic import BaseModel, Field, PositiveInt, field_serializer


class StatusInternetOut(BaseModel):
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
    id: PositiveInt = Field(description="ID do contrato.", examples=[1])
    id_login: PositiveInt = Field(description="ID do login.", examples=[12])
    id_cliente: PositiveInt = Field(description="ID do cliente.", examples=[123])
    nome_cliente: str = Field(
        description="Nome do cliente.", examples=["Nome do cliente"]
    )
    status: utils.StatusContratoCod = Field(
        description="Status do contrato.",
        examples=[utils.StatusContratoRot.PRE_CONTRATO],
    )
    contrato: str = Field(description="Nome do plano.", examples=["Nome do plano"])
    valor: float = Field(description="Valor do plano.", examples=[12.34])
    data_vencimento: str = Field(
        description="Data de vencimento.", examples=["YYYY-MM-AA"]
    )
    mac_onu: str = Field(description="MAC da ONU.", examples=["AB1..."])

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
    meta: Meta


class ComercialContrato(BaseModel):
    id: PositiveInt = Field(description="ID do contrato.", examples=[1])
    contrato: str = Field(description="Nome do plano.", examples=["Nome do plano"])
    nome_cliente: str = Field(
        description="Nome do cliente.", examples=["Nome do cliente"]
    )
    valor: float = Field(description="Valor do plano.", examples=[12.34])
    status_acesso: utils.StatusInternetCod = Field(
        description="Status do acesso.", examples=[utils.StatusInternetRot.ATIVO]
    )
    data_vencimento: str = Field(
        description="Data de vencimento.", examples=["YYYY-MM-AA"]
    )
    id_cliente: PositiveInt = Field(description="ID do cliente.", examples=[12])
    id_login: PositiveInt = Field(description="ID do login.", examples=[123])

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
    meta: Meta


class VilaContratoOut(BaseModel):
    id: PositiveInt = Field(description="ID do contrato.", examples=[1])
    id_login: PositiveInt = Field(description="ID do login.", examples=[12])
    id_cliente: PositiveInt = Field(description="ID do cliente.", examples=[123])
