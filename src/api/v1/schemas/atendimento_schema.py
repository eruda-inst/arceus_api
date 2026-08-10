from pydantic import BaseModel, Field, NonNegativeInt, field_serializer

from .. import utils


class AtendimentoInSchema(BaseModel):
    # IDs NonNegativeInt, pois o IXC é quebrado
    id_login: NonNegativeInt = Field(description="ID de login", examples=[1])
    id_assunto: NonNegativeInt = Field(description="ID do assunto", examples=[12])
    id_cliente: NonNegativeInt = Field(description="ID do cliente", examples=[123])
    mensagem: str = Field(
        description="Mensagem do atendimento", examples=["Mensagem do atendimento"]
    )
    origem_endereco: utils.OrigemEnderecoCod | None = Field(
        default=utils.OrigemEnderecoCod.LOGIN,
        description="Origem do endereço",
        examples=[utils.OrigemEnderecoCod.LOGIN],
    )
    tipo: utils.TipoAtendimentoCod | None = Field(
        default=utils.TipoAtendimentoCod.CLIENTE,
        description="Tipo do atendimento",
        examples=[utils.TipoAtendimentoCod.CLIENTE],
    )
    titulo: str = Field(
        description="Título do atendimento", examples=["Título do atendimento"]
    )
    prioridade: utils.PrioridadeCod | None = Field(
        default=utils.PrioridadeCod.NORMAL,
        description="Pioridade do atendimento",
        examples=[utils.PrioridadeCod.NORMAL],
    )
    su_status: utils.SuStatusCod | None = Field(
        default=utils.SuStatusCod.NOVO,
        description="Status do atendimento",
        examples=[utils.SuStatusCod.NOVO],
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


class AtendimentoOutSchema(BaseModel):
    # IDs NonNegativeInt, pois o IXC é quebrado
    id: NonNegativeInt = Field(description="ID do atendimento", examples=[1])
    id_assunto: NonNegativeInt = Field(description="ID do assunto", examples=[12])
    status: utils.SuStatusCod = Field(
        description="Status do atendimento", examples=[utils.SuStatusRot.NOVO]
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
    def serialize_status(self, v: utils.SuStatusCod) -> utils.SuStatusRot:
        cod = utils.SuStatusCod
        rot = utils.SuStatusRot

        mapping = {
            cod.NOVO: rot.NOVO,
            cod.PENDENTE: rot.PENDENTE,
            cod.EM_PROGRESSO: rot.EM_PROGRESSO,
            cod.SOLUCIONADO: rot.SOLUCIONADO,
            cod.CANCELADO: rot.CANCELADO,
        }

        return mapping[v]

    @field_serializer("data_criacao")
    def serialize_data_criacao(self, v: str) -> str:
        return utils.Formatter.data(data=v)
