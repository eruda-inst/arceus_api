from pydantic import BaseModel, Field, computed_field

from .misc_schema import Meta


class PlanoSugeridoOut(BaseModel):
    nome_plano_atual: str = Field(
        description="Nome do plano antigo",
        examples=["Nome do plano antigo"],
    )
    valor_plano_atual: float = Field(
        description="Valor do plano antigo", examples=[12.34]
    )
    nome_plano_sugerido: str = Field(
        description="Nome do plano sugerido",
        examples=["Nome do plano sugerido"],
    )
    valor_plano_sugerido: float = Field(
        description="Valor do plano sugerido", examples=[12.34]
    )

    @computed_field
    @property
    def valor_acrescimo(self) -> float:
        valor_acrescimo = self.valor_plano_sugerido - self.valor_plano_atual

        if valor_acrescimo <= 0.00:
            return 0.00

        return round(valor_acrescimo, 2)


class PlanoSugeridoListOut(BaseModel):
    data: list[PlanoSugeridoOut]
    meta: Meta
