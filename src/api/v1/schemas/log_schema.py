from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class LogOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt = Field(description="ID do log", examples=[1])
    metodo: str = Field(description="Método HTTP da requisição", examples=["GET"])
    endpoint: str = Field(
        description="Endpoint da requisição", examples=["/vila/status_onu"]
    )
    codigo: PositiveInt = Field(description="Código HTTP da resposta", examples=[200])
    duracao: float = Field(
        description="Duração entre requisição, processamento e resposta",
        examples=[0.234],
    )
    url: str = Field(
        description="URL completa ou path do registro",
        examples=["http://localhost/api/v1/vila/status_onu"],
    )
    protocolo: str | None = Field(
        default=None, description="Protocolo do OPA", examples=["NWT123456789"]
    )
    payload: str | None = Field(
        default=None, description="Payload da requisição", examples=["{...}"]
    )
    resposta: str = Field(description="Resposta", examples=["{...}"])
    setor: str = Field(
        description="Setor envolvido na requisição",
        examples=["SUPPORT"],
    )
    nome_cliente: str | None = Field(
        default=None, description="Nome do cliente", examples=["Nome do cliente"]
    )
    criado_em: datetime = Field(
        description="Data de criação do grupo", examples=["AAAA-MM-DD HH:MM:SS"]
    )
