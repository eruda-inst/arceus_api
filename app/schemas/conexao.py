from pydantic import BaseModel, Field
from ..utils.helpers.rotular import StatusConexaoRotulo


class StatusConexao(BaseModel):
    status_conexao: StatusConexaoRotulo = Field(description="Status da conexão.")


class StatusConexaoOut(BaseModel):
    data: StatusConexao