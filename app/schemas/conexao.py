from typing import Literal
from pydantic import BaseModel
from app.utils.helpers.rotular import StatusConexaoRotulo


class StatusConexao(BaseModel):
    status_conexao: StatusConexaoRotulo


class StatusConexaoOut(BaseModel):
    data: StatusConexao