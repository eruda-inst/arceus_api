from .. import utils
from . import misc_schema
from pydantic import BaseModel, Field, PositiveInt, field_serializer


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
