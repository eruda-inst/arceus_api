from typing import Optional
from pydantic import Field, BaseModel


class Meta(BaseModel):
    total: int = Field(
        ge=1,
        description="Número total de itens em todas as páginas.",
    )
    page: Optional[int] = Field(
        default=1,
        ge=1,
        description="Número da página atual na sequência de paginação.",
    )
    per_page: Optional[int] = Field(
        default=10,
        ge=1,
        description="Número de itens exibidos por página.",
    )


class Links(BaseModel):
    self: str = Field(
        description="URL da página atual de resultados.",
    )
    next: Optional[str] = Field(
        default=None,
        description="URL para a próxima página de resultados, se disponível.",
    )
    prev: Optional[str] = Field(
        default=None,
        description="URL para a página anterior de resultados, se disponível.",
    )
