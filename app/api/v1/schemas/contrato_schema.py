from . import Meta
from .. import utils
from pydantic import BaseModel, Field, field_serializer, NonNegativeInt


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


class ContratoOut(BaseModel):
    # IDs NonNegativeInt, pois o IXC é quebrado
    id: NonNegativeInt = Field(description="ID do contrato.", examples=[1])
    id_login: NonNegativeInt = Field(description="ID do login.", examples=[12])
    id_cliente: NonNegativeInt = Field(description="ID do cliente.", examples=[123])
    nome_cliente: str = Field(
        description="Nome do cliente.", examples=["Nome do cliente"]
    )
    status: utils.StatusContratoCod = Field(
        description="Status do contrato.",
        examples=[utils.StatusContratoRot.PRE_CONTRATO],
    )
    status_acesso: utils.StatusInternetCod = Field(
        description="Status de acesso.", examples=[utils.StatusInternetRot.ATIVO]
    )
    nome_plano: str = Field(description="Nome do plano.", examples=["Nome do plano"])
    valor_fatura: float = Field(description="Valor da fatura.", examples=[12.34])
    dia_vencimento_fatura: str = Field(
        description="Dia de vencimento da fatura.", examples=["01"]
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

    @field_serializer("status_acesso")
    def serialize_status_acesso(
        self, v: utils.StatusInternetCod
    ) -> utils.StatusInternetRot:
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
    data: list[ContratoOut]
    meta: Meta


class ComercialContratoOut(BaseModel):
    # IDs NonNegativeInt, pois o IXC é quebrado
    id: NonNegativeInt = Field(description="ID do contrato.", examples=[1])
    nome_plano: str = Field(description="Nome do plano.", examples=["Nome do plano"])
    nome_cliente: str = Field(
        description="Nome do cliente.", examples=["Nome do cliente"]
    )
    valor_fatura: float = Field(description="Valor do plano.", examples=[12.34])
    status_acesso: utils.StatusInternetCod = Field(
        description="Status do acesso.", examples=[utils.StatusInternetRot.ATIVO]
    )
    dia_vencimento_fatura: str = Field(
        description="Dia de vencimento da fatura.", examples=["01"]
    )
    id_cliente: NonNegativeInt = Field(description="ID do cliente.", examples=[12])
    id_login: NonNegativeInt = Field(description="ID do login.", examples=[123])

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
    data: list[ComercialContratoOut]
    meta: Meta


class VilaContratoOut(BaseModel):
    # IDs NonNegativeInt, pois o IXC é quebrado
    id: NonNegativeInt = Field(description="ID do contrato.", examples=[1])
    id_login: NonNegativeInt = Field(description="ID do login.", examples=[12])
    id_cliente: NonNegativeInt = Field(description="ID do cliente.", examples=[123])
