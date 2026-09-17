from pydantic import BaseModel, Field, NonNegativeInt, PositiveInt, field_serializer

from .. import utils


class InternetStatusOutSchema(BaseModel):
    status_acesso: utils.InternetStatusCode = Field(
        description="Status de acesso", examples=[utils.InternetStatusLabel.ACTIVE]
    )

    @field_serializer("status_acesso")
    def serialize_status(
        self, v: utils.InternetStatusCode
    ) -> utils.InternetStatusLabel:
        cod = utils.InternetStatusCode
        rot = utils.InternetStatusLabel

        mapping = {
            cod.ACTIVE: rot.ACTIVE,
            cod.DEACTIVATED: rot.DEACTIVATED,
            cod.MANUAL_BLOCK: rot.MANUAL_BLOCK,
            cod.AUTOMATIC_BLOCK: rot.AUTOMATIC_BLOCK,
            cod.FINANCIAL_OVERDUE: rot.FINANCIAL_OVERDUE,
            cod.AWAITING_SIGNATURE: rot.AWAITING_SIGNATURE,
        }

        return mapping[v]


class ContractOutSchema(BaseModel):
    # IDs NonNegativeInt, pois o IXC é quebrado
    id: NonNegativeInt = Field(description="ID do contrato", examples=[1])
    id_login: NonNegativeInt | None = Field(description="ID do login", examples=[12])
    id_cliente: NonNegativeInt = Field(description="ID do cliente", examples=[123])
    nome_cliente: str = Field(
        description="Nome do cliente", examples=["Nome do cliente"]
    )
    status: utils.ContractStatusCode = Field(
        description="Status do contrato",
        examples=[utils.ContractStatusLabel.PRE_CONTRACT],
    )
    status_acesso: utils.InternetStatusCode = Field(
        description="Status de acesso", examples=[utils.InternetStatusLabel.ACTIVE]
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
    def serialize_status(
        self, v: utils.ContractStatusCode
    ) -> utils.ContractStatusLabel:
        cod = utils.ContractStatusCode
        rot = utils.ContractStatusLabel

        mapping = {
            cod.PRE_CONTRACT: rot.PRE_CONTRACT,
            cod.ACTIVE: rot.ACTIVE,
            cod.INACTIVE: rot.INACTIVE,
            cod.NEGATIVE: rot.NEGATIVE,
            cod.WITHDREW: rot.WITHDREW,
        }

        return mapping[v]

    @field_serializer("status_acesso")
    def serialize_status_acesso(
        self, v: utils.InternetStatusCode
    ) -> utils.InternetStatusLabel:
        cod = utils.InternetStatusCode
        rot = utils.InternetStatusLabel

        mapping = {
            cod.ACTIVE: rot.ACTIVE,
            cod.DEACTIVATED: rot.DEACTIVATED,
            cod.MANUAL_BLOCK: rot.MANUAL_BLOCK,
            cod.AUTOMATIC_BLOCK: rot.AUTOMATIC_BLOCK,
            cod.FINANCIAL_OVERDUE: rot.FINANCIAL_OVERDUE,
            cod.AWAITING_SIGNATURE: rot.AWAITING_SIGNATURE,
        }

        return mapping[v]


class VillageContractOutSchema(BaseModel):
    # IDs NonNegativeInt, pois o IXC é quebrado
    id: NonNegativeInt = Field(description="ID do contrato", examples=[1])
    id_login: NonNegativeInt = Field(description="ID do login", examples=[12])
    id_cliente: NonNegativeInt = Field(description="ID do cliente", examples=[123])
