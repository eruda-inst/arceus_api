from typing import Literal
from pydantic import BaseModel


class StatusConexao(BaseModel):
    status_conexao: Literal["S", "SS", "N"]


class StatusConexaoOut(BaseModel):
    data: StatusConexao