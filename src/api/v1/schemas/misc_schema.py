from typing import TypeVar

from pydantic import BaseModel, Field, NonNegativeInt, PositiveInt, computed_field

T = TypeVar("T")


class MetaOutSchema(BaseModel):
    pagina_atual: PositiveInt = Field(ge=1, description="Página atual")
    itens_por_pagina: PositiveInt = Field(ge=1, description="Itens por página")
    total_itens: NonNegativeInt = Field(ge=0, description="Total de itens")

    @computed_field
    @property
    def total_paginas(self) -> int:
        if self.total_itens == 0:
            return 0
        # Divisão inteira arredondando para cima
        return (self.total_itens + self.itens_por_pagina - 1) // self.itens_por_pagina


class ListOutSchema[T](BaseModel):
    data: list[T]
    meta: MetaOutSchema


class TodayAlwaysOutSchema[T](BaseModel):
    hoje: T
    sempre: T


class MensagemOutSchema(BaseModel):
    mensagem: str = Field(
        description="Mensagem de retorno", examples=["Mensagem de retorno"]
    )
