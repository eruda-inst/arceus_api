from typing import Optional
from pydantic import Field, BaseModel, PositiveInt


class Meta(BaseModel):
    total: PositiveInt = Field(
        description="Número total de itens em todas as páginas.", ge=1, examples=[1]
    )
    page: Optional[PositiveInt] = Field(
        default=1,
        description="Número da página atual na sequência de paginação.",
        examples=[1],
    )
    per_page: Optional[PositiveInt] = Field(
        default=10, description="Número de itens exibidos por página.", examples=[10]
    )


class MensagemOut(BaseModel):
    mensagem: str = Field(
        description="Mensagem de sucesso.", examples=["Operação realizada com sucesso."]
    )
