from pydantic import Field, BaseModel, NonNegativeInt, PositiveInt


class Meta(BaseModel):
    total_itens: NonNegativeInt = Field(
        description="Número total de itens em todas as páginas.", ge=1, examples=[1]
    )
    pagina_atual: PositiveInt | None = Field(
        default=1,
        description="Número da página atual na sequência de paginação.",
        examples=[1],
    )
    itens_por_pagina: PositiveInt | None = Field(
        default=10, description="Número de itens exibidos por página.", examples=[10]
    )


class MensagemOut(BaseModel):
    mensagem: str = Field(
        description="Mensagem de retorno.", examples=["Mensagem de retorno"]
    )
