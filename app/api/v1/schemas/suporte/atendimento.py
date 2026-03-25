from .. import misc
from app.api.v1 import utils
from typing import Optional, List
from pydantic import BaseModel, Field, PositiveInt


class AtendimentoCreate(BaseModel):
    id: PositiveInt = Field(description="ID do atendimento aberto.", examples=[123])


class AtendimentoIn(BaseModel):
    id_login: PositiveInt = Field(description="ID de login do cliente.", examples=[123])
    id_assunto: PositiveInt = Field(
        description="ID do assunto do atendimento.", examples=[1]
    )
    id_cliente: PositiveInt = Field(description="ID do cliente.", examples=[456])
    menssagem: str = Field(
        description="Mensagem descritiva.", examples=["Estou com problemas."]
    )
    origem_endereco: Optional[utils.OrigemEnderecoCod] = Field(
        default=utils.OrigemEnderecoCod.LOGIN,
        description="Origem de endereço.",
        examples=[utils.OrigemEnderecoCod.LOGIN],
    )
    tipo: Optional[utils.TipoCod] = Field(
        default=utils.TipoCod.CLIENTE,
        description="Tipo do atendimento.",
        examples=[utils.TipoCod.CLIENTE],
    )
    titulo: str = Field(
        description="Título do atendimento.", examples=["Problema de conexão."]
    )
    prioridade: Optional[utils.PrioridadeCod] = Field(
        default=utils.PrioridadeCod.NORMAL,
        description="Pioridade do atendimento.",
        examples=[utils.PrioridadeCod.NORMAL],
    )
    su_status: Optional[utils.SuStatusCod] = Field(
        default=utils.SuStatusCod.NOVO,
        description="Status do atendimento.",
        examples=[utils.SuStatusCod.NOVO],
    )
    id_ticket_setor: Optional[PositiveInt] = Field(
        default=utils.Default.ID_TICKET_SETOR,
        description="Setor do atendimento.",
        examples=[2],
    )
    id_contrato: PositiveInt = Field(
        description="ID de contrato do cliente.", examples=[789]
    )
    id_responsavel_tecnico: Optional[PositiveInt] = Field(
        default=utils.Default.ID_RESPONSAVEL_ARCEUS,
        description="ID do responsável técnico.",
        examples=[987],
    )


class Atendimento(BaseModel):
    id: PositiveInt = Field(description="ID do atendimento.", examples=[123])
    id_assunto: PositiveInt = Field(
        description="ID do assunto do atendimento.", examples=[1]
    )
    status: utils.StatusAtendimentoRot = Field(
        description="Status do atendimento.", examples=[utils.StatusAtendimentoRot.NOVO]
    )
    mensagem: str = Field(
        max_length=999,
        description="Mensagem descritiva.",
        examples=["Estou com problemas de conexão na minha residência."],
    )
    titulo: str = Field(
        max_length=200,
        description="Título do atendimento.",
        examples=["Problema de conexão"],
    )
    data_criacao: str = Field(
        description="Data de criação do atendimento.", examples=["2025-12-31 12:00:00"]
    )


class AtendimentoOut(BaseModel):
    data: List[Atendimento] = Field()
    meta: misc.Meta = Field()
