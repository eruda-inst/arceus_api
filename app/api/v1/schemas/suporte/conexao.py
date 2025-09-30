from pydantic import BaseModel, Field
from app.api.v1 import utils


class StatusConexao(BaseModel):
    status_conexao: utils.StatusConexaoRot = Field(description="Status da conexão.")


class StatusConexaoOut(BaseModel):
    data: StatusConexao
