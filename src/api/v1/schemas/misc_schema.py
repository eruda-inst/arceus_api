from typing import Generic, TypeVar

from pydantic import BaseModel, Field, NonNegativeInt, PositiveInt

T = TypeVar("T")


class MetaOut(BaseModel):
    pagina_atual: PositiveInt = Field(ge=1, description="Página atual")
    itens_por_pagina: PositiveInt = Field(ge=1, description="Itens por página")
    total_paginas: NonNegativeInt = Field(ge=0, description="Total de páginas")
    total_itens: NonNegativeInt = Field(ge=0, description="Total de itens")


class ListOut(BaseModel, Generic[T]):
    data: list[T]
    meta: MetaOut


class TodayAlwaysOut(BaseModel, Generic[T]):
    hoje: T
    sempre: T


class Meta(BaseModel):
    total_itens: NonNegativeInt = Field(
        description="Número total de itens em todas as páginas", ge=1, examples=[1]
    )
    pagina_atual: PositiveInt | None = Field(
        default=1,
        description="Número da página atual na sequência de paginação",
        examples=[1],
    )
    itens_por_pagina: PositiveInt | None = Field(
        default=10, description="Número de itens exibidos por página", examples=[10]
    )


class MensagemOut(BaseModel):
    mensagem: str = Field(
        description="Mensagem de retorno", examples=["Mensagem de retorno"]
    )
