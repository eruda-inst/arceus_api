from pydantic import BaseModel, Field, NonNegativeInt, field_serializer

from .. import utils


class TicketInSchema(BaseModel):
    # IDs NonNegativeInt, pois o IXC é quebrado
    id_login: NonNegativeInt = Field(description="ID de login", examples=[1])
    id_assunto: NonNegativeInt = Field(description="ID do assunto", examples=[12])
    id_cliente: NonNegativeInt = Field(description="ID do cliente", examples=[123])
    mensagem: str = Field(
        description="Mensagem do atendimento", examples=["Mensagem do atendimento"]
    )
    origem_endereco: utils.AddressOriginCode | None = Field(
        default=utils.AddressOriginCode.LOGIN,
        description="Origem do endereço",
        examples=[utils.AddressOriginCode.LOGIN],
    )
    tipo: utils.TicketTypeCode | None = Field(
        default=utils.TicketTypeCode.CUSTOMER,
        description="Tipo do atendimento",
        examples=[utils.TicketTypeCode.CUSTOMER],
    )
    titulo: str = Field(
        description="Título do atendimento", examples=["Título do atendimento"]
    )
    prioridade: utils.PriorityCode | None = Field(
        default=utils.PriorityCode.NORMAL,
        description="Pioridade do atendimento",
        examples=[utils.PriorityCode.NORMAL],
    )
    su_status: utils.SupportStatusCode | None = Field(
        default=utils.SupportStatusCode.NEW,
        description="Status do atendimento",
        examples=[utils.SupportStatusCode.NEW],
    )
    id_ticket_setor: NonNegativeInt | None = Field(
        default=utils.Default.ID_TICKET_SETOR,
        description="Setor do atendimento",
        examples=[utils.Default.ID_TICKET_SETOR],
    )
    id_contrato: NonNegativeInt = Field(description="ID do contrato", examples=[1234])
    id_responsavel_tecnico: NonNegativeInt | None = Field(
        default=utils.Default.ID_RESPONSAVEL_ARCEUS,
        description="ID do responsável técnico",
        examples=[utils.Default.ID_RESPONSAVEL_ARCEUS],
    )


class TicketOutSchema(BaseModel):
    # IDs NonNegativeInt, pois o IXC é quebrado
    id: NonNegativeInt = Field(description="ID do atendimento", examples=[1])
    id_assunto: NonNegativeInt = Field(description="ID do assunto", examples=[12])
    status: utils.SupportStatusCode = Field(
        description="Status do atendimento", examples=[utils.SupportStatusLabel.NEW]
    )
    mensagem: str = Field(
        description="Mensagem do atendimento", examples=["Mensagem do atendimento"]
    )
    titulo: str = Field(
        description="Título do atendimento", examples=["Título do atendimento"]
    )
    data_criacao: str = Field(
        description="Data de criação do atendimento",
        # Não pode haver isto, pois o IXC é quebrado
        # min_length=10,  # DD/MM/AAAA
        # max_length=10,  # DD/MM/AAAA
        examples=["DD/MM/AAAA"],
    )

    @field_serializer("status")
    def serialize_status(self, v: utils.SupportStatusCode) -> utils.SupportStatusLabel:
        cod = utils.SupportStatusCode
        rot = utils.SupportStatusLabel

        mapping = {
            cod.NEW: rot.NEW,
            cod.PENDING: rot.PENDING,
            cod.IN_PROGRESS: rot.IN_PROGRESS,
            cod.SOLVED: rot.SOLVED,
            cod.CANCELED: rot.CANCELED,
        }

        return mapping[v]

    @field_serializer("data_criacao")
    def serialize_data_criacao(self, v: str) -> str:
        return utils.Formatter.date(date=v)
