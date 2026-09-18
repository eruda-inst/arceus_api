"""
Pydantic schemas for group-related responses.
"""

import datetime as dt

from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class GroupOutSchema(BaseModel):
    """
    Response schema for group details.
    """

    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt = Field(ge=1, description="ID do grupo", examples=[1])
    nome: str = Field(description="Nome do grupo", examples=["Nome do grupo"])
    criado_em: dt.datetime = Field(
        description="Data de criação do grupo", examples=["AAAA-MM-DD HH:MM:SS"]
    )
