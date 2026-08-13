from pydantic import BaseModel, Field, NonNegativeInt, PositiveInt, field_serializer

from .. import utils


class StatusInternetOutSchema(BaseModel):
    status_acesso: utils.StatusInternetCod = Field(
        description="Status de acesso", examples=[utils.StatusInternetRot.ATIVO]
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


class ContratoOutSchema(BaseModel):
    # IDs NonNegativeInt, pois o IXC é quebrado
    id: NonNegativeInt = Field(description="ID do contrato", examples=[1])
    id_login: NonNegativeInt | None = Field(description="ID do login", examples=[12])
    id_cliente: NonNegativeInt = Field(description="ID do cliente", examples=[123])
    nome_cliente: str = Field(
        description="Nome do cliente", examples=["Nome do cliente"]
    )
    status: utils.StatusContratoCod = Field(
        description="Status do contrato",
        examples=[utils.StatusContratoRot.PRE_CONTRATO],
    )
    status_acesso: utils.StatusInternetCod = Field(
        description="Status de acesso", examples=[utils.StatusInternetRot.ATIVO]
    )
    nome_plano: str = Field(description="Nome do plano", examples=["Nome do plano"])
    valor_fatura: float | None = Field(
        default=None, description="Valor da fatura", examples=[12.34]
    )
    dia_vencimento_fatura: PositiveInt | None = Field(
        default=None,
        description="Dia de vencimento da fatura",
        ge=1,
        le=31,
        examples=[1],
    )
    mac_onu: str | None = Field(
        default=None, description="MAC da ONU", examples=["AB1..."]
    )

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


class VilaContratoOutSchema(BaseModel):
    # IDs NonNegativeInt, pois o IXC é quebrado
    id: NonNegativeInt = Field(description="ID do contrato", examples=[1])
    id_login: NonNegativeInt = Field(description="ID do login", examples=[12])
    id_cliente: NonNegativeInt = Field(description="ID do cliente", examples=[123])
