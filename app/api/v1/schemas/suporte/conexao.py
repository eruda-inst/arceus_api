from app.api.v1 import utils
from pydantic import BaseModel, Field


class StatusConexao(BaseModel):
    status_conexao: utils.StatusConexaoRot = Field(
        description="Status da conexão.", examples=[utils.StatusConexaoRot.CONECTADO]
    )


class StatusConexaoOut(BaseModel):
    data: StatusConexao = Field()
