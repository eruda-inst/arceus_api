from app.api.v1 import utils
from pydantic import BaseModel, Field


class StatusConexao(BaseModel):
    status_conexao: utils.StatusConexaoRot = Field(description="Status da conexão.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status_conexao": utils.StatusConexaoRot.CONECTADO,
                }
            ]
        }
    }


class StatusConexaoOut(BaseModel):
    data: StatusConexao

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "data": {
                        "status_conexao": utils.StatusConexaoRot.CONECTADO,
                    }
                }
            ]
        }
    }
