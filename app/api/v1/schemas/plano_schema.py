from . import Meta
from pydantic import BaseModel, Field


class PlanoSugeridoOut(BaseModel):
    nome_plano_atual: str = Field(
        description="Nome do plano antigo.",
        examples=["Nome do plano antigo"],
    )
    valor_plano_atual: float = Field(
        description="Valor do plano antigo.", examples=[12.34]
    )
    nome_plano_sugerido: str = Field(
        description="Nome do plano sugerido.",
        examples=["Nome do plano sugerido"],
    )
    valor_plano_sugerido: float = Field(
        description="Valor do plano sugerido.", examples=[12.34]
    )


class PlanoSugeridoListOut(BaseModel):
    data: list[PlanoSugeridoOut]
    meta: Meta
