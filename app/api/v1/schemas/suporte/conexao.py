from pydantic import BaseModel, Field
from app.api.v1.utils import StatusConexaoRot


class StatusConexao(BaseModel):
    status_conexao: StatusConexaoRot = Field(description="Status da conexão.")


class StatusConexaoOut(BaseModel):
    data: StatusConexao
