from .. import utils
from . import misc_schema
from pydantic import BaseModel, Field, PositiveInt, field_serializer


class AtendimentoCreate(BaseModel):
    id: PositiveInt = Field(description="ID do atendimento aberto.", examples=[1])


class AtendimentoIn(BaseModel):
    id_login: PositiveInt = Field(description="ID de login do cliente.", examples=[1])
    id_assunto: PositiveInt = Field(
        description="ID do assunto do atendimento.", examples=[1]
    )
    id_cliente: PositiveInt = Field(description="ID do cliente.", examples=[1])
    menssagem: str = Field(
        description="Mensagem descritiva.", examples=["Estou com problemas."]
    )
    origem_endereco: utils.OrigemEnderecoCod | None = Field(
        default=utils.OrigemEnderecoCod.LOGIN,
        description="Origem de endereço.",
        examples=[utils.OrigemEnderecoCod.LOGIN],
    )
    tipo: utils.TipoCod | None = Field(
        default=utils.TipoCod.CLIENTE,
        description="Tipo do atendimento.",
        examples=[utils.TipoCod.CLIENTE],
    )
    titulo: str = Field(
        description="Título do atendimento.", examples=["Problema de conexão."]
    )
    prioridade: utils.PrioridadeCod | None = Field(
        default=utils.PrioridadeCod.NORMAL,
        description="Pioridade do atendimento.",
        examples=[utils.PrioridadeCod.NORMAL],
    )
    su_status: utils.SuStatusCod | None = Field(
        default=utils.SuStatusCod.NOVO,
        description="Status do atendimento.",
        examples=[utils.SuStatusCod.NOVO],
    )
    id_ticket_setor: PositiveInt | None = Field(
        default=utils.Default.ID_TICKET_SETOR,
        description="Setor do atendimento.",
        examples=[utils.Default.ID_TICKET_SETOR],
    )
    id_contrato: PositiveInt = Field(
        description="ID de contrato do cliente.", examples=[1]
    )
    id_responsavel_tecnico: PositiveInt | None = Field(
        default=utils.Default.ID_RESPONSAVEL_ARCEUS,
        description="ID do responsável técnico.",
        examples=[utils.Default.ID_RESPONSAVEL_ARCEUS],
    )


class Atendimento(BaseModel):
    id: PositiveInt = Field(description="ID do atendimento.", examples=[1])
    id_assunto: PositiveInt = Field(
        description="ID do assunto do atendimento.", examples=[1]
    )
    status: utils.SuStatusCod = Field(
        description="Status do atendimento.", examples=[utils.SuStatusRot.NOVO]
    )
    mensagem: str = Field(
        description="Mensagem descritiva.",
        examples=["Estou com problemas de conexão na minha residência."],
    )
    titulo: str = Field(
        description="Título do atendimento.", examples=["Problema de conexão"]
    )
    data_criacao: str = Field(
        description="Data de criação do atendimento.",
        examples=["YYYY-MM-DDTHH:mm:ss.sssZ"],
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


class AtendimentoOut(BaseModel):
    data: list[Atendimento]
    meta: misc_schema.Meta
