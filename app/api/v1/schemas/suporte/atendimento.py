from .. import misc
from app.api.v1 import utils
from typing import Optional, List
from pydantic import BaseModel, Field, PositiveInt


class AtendimentoCreate(BaseModel):
    id: PositiveInt = Field(description="ID do atendimento aberto.")

    model_config = {"json_schema_extra": {"example": {"id": 123}}}


class AtendimentoIn(BaseModel):
    id_login: PositiveInt = Field(description="ID de login do cliente.")
    id_assunto: PositiveInt = Field(description="ID do assunto do atendimento.")
    id_cliente: PositiveInt = Field(description="ID do cliente.")
    menssagem: str = Field(description="Mensagem descritiva.")
    origem_endereco: Optional[utils.OrigemEnderecoCod] = Field(
        default=utils.OrigemEnderecoCod.LOGIN, description="Origem de endereço."
    )
    tipo: Optional[utils.TipoCod] = Field(
        default=utils.TipoCod.CLIENTE, description="Tipo do atendimento."
    )
    titulo: str = Field(description="Título do atendimento.")
    prioridade: Optional[utils.PrioridadeCod] = Field(
        default=utils.PrioridadeCod.NORMAL, description="Pioridade do atendimento."
    )
    su_status: Optional[utils.SuStatusCod] = Field(
        default=utils.SuStatusCod.NOVO, description="Status do atendimento."
    )
    id_ticket_setor: Optional[PositiveInt] = Field(
        default=utils.Default.ID_TICKET_SETOR, description="Setor do atendimento."
    )
    id_contrato: PositiveInt = Field(description="ID de contrato do cliente.")
    id_responsavel_tecnico: Optional[PositiveInt] = Field(
        default=utils.Default.ID_RESPONSAVEL_ARCEUS,
        description="ID do responsável técnico.",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id_login": 123,
                "id_assunto": 1,
                "id_cliente": 456,
                "menssagem": "Estou com problemas de conexão na minha residência.",
                "origem_endereco": utils.OrigemEnderecoCod.LOGIN,
                "tipo": utils.TipoCod.CLIENTE,
                "titulo": "Problema de conexão",
                "prioridade": utils.PrioridadeCod.ALTA,
                "su_status": utils.SuStatusCod.NOVO,
                "id_ticket_setor": 2,
                "id_contrato": 789,
                "id_responsavel_tecnico": 987,
            }
        }
    }


class Atendimento(BaseModel):
    id: PositiveInt = Field(description="ID do atendimento.")
    id_assunto: PositiveInt = Field(description="ID do assunto do atendimento.")
    status: utils.StatusAtendimentoRot = Field(description="Status do atendimento.")
    mensagem: str = Field(max_length=999, description="Mensagem descritiva.")
    titulo: str = Field(max_length=200, description="Título do atendimento.")
    data_criacao: str = Field(description="Data de criação do atendimento.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 123,
                "id_assunto": 1,
                "status": utils.StatusAtendimentoCod.NOVO,
                "mensagem": "Estou com problemas de conexão na minha residência.",
                "titulo": "Problema de conexão",
                "data_criacao": "2025-12-31 12:00:00",
            }
        }
    }


class AtendimentoOut(BaseModel):
    data: List[Atendimento]
    meta: misc.Meta

    model_config = {
        "json_schema_extra": {
            "example": {
                "data": [
                    {
                        "id": 123,
                        "id_assunto": 1,
                        "status": utils.StatusAtendimentoRot.NOVO,
                        "mensagem": "Estou com problemas de conexão na minha residência.",
                        "titulo": "Problema de conexão",
                        "data_criacao": "2025-12-31 12:00:00",
                    },
                    {
                        "id": 124,
                        "id_assunto": 1,
                        "status": utils.StatusAtendimentoRot.NOVO,
                        "mensagem": "Estou com problemas de conexão na minha residência.",
                        "titulo": "Problema de conexão",
                        "data_criacao": "2025-12-31 12:00:00",
                    },
                ],
                "meta": {"total": 2, "page": 1, "per_page": 10},
            }
        }
    }
