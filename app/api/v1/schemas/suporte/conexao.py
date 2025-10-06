from app.api.v1 import utils
from pydantic import BaseModel, Field


class StatusConexao(BaseModel):
    status_conexao: utils.StatusConexaoRot = Field(description="Status da conexão.")


class StatusConexaoOut(BaseModel):
    data: StatusConexao
