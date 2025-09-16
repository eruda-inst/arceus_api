from ..utils import StatusConexaoRot
from pydantic import BaseModel, Field


class StatusConexao(BaseModel):
    status_conexao: StatusConexaoRot = Field(description="Status da conexão.")

class StatusConexaoOut(BaseModel):
    data: StatusConexao