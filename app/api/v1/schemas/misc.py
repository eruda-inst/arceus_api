from typing import Optional
from pydantic import Field, BaseModel, PositiveInt


class Meta(BaseModel):
    total: PositiveInt = Field(description="Número total de itens em todas as páginas.")
    page: Optional[PositiveInt] = Field(
        default=1, description="Número da página atual na sequência de paginação."
    )
    per_page: Optional[PositiveInt] = Field(
        default=10, description="Número de itens exibidos por página."
    )


class Links(BaseModel):
    self: str = Field(description="URL da página atual de resultados.")
    next: Optional[str] = Field(
        default=None,
        description="URL para a próxima página de resultados, se disponível.",
    )
    prev: Optional[str] = Field(
        default=None,
        description="URL para a página anterior de resultados, se disponível.",
    )


class MensagemOut(BaseModel):
    mensagem: str = Field(description="Mensagem de sucesso.")
