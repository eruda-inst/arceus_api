from .. import utils
from pydantic import BaseModel, field_serializer, Field


class StatusConexaoOut(BaseModel):
    status_conexao: utils.StatusConexaoCod = Field(
        description="Status da conexão.", examples=[utils.StatusConexaoRot.CONECTADO]
    )

    @field_serializer("status_conexao")
    def serialize_status_conexao(self, v: utils.StatusConexaoCod):
        Cod = utils.StatusConexaoCod
        Rot = utils.StatusConexaoRot

        mapping = {
            Cod.CONECTADO: Rot.CONECTADO,
            Cod.DESCONECTADO: Rot.DESCONECTADO,
            Cod.SEM_STATUS: Rot.SEM_STATUS,
        }

        return mapping[v]
