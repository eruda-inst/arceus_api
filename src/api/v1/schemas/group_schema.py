from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class GroupOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt = Field(ge=1, description="ID do grupo", examples=[1])
    nome: str = Field(description="Nome do grupo", examples=["Nome do grupo"])
    criado_em: datetime = Field(
        description="Data de criação do grupo", examples=["AAAA-MM-DD HH:MM:SS"]
    )
