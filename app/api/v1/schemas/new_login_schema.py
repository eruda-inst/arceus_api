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

        s = Rot.CONECTADO
        s = Rot.DESCONECTADO if v == Cod.DESCONECTADO else s
        s = Rot.SEM_STATUS if v == Cod.SEM_STATUS else s

        return s
