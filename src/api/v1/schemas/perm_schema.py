from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class PermOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt = Field(ge=1, description="ID da permissão", examples=[1])
    nome: str = Field(description="Nome da permissão", examples=["Nome da permissão"])
    codigo: str = Field(
        description="Código da permissão", examples=["codigo:permissao"]
    )
    criado_em: datetime = Field(
        description="Data de criação da permissão",
        examples=["AAAA-MM-DD HH:MM:SS"],
    )
