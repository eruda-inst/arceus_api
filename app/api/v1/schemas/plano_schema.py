from . import misc_schema
from pydantic import BaseModel, Field


class PlanoSugeridoOut(BaseModel):
    nome_plano_atual: str = Field(
        description="Nome do plano de venda antigo.",
        examples=["NEWNET PADRAO - 250MB - 06/2025"],
    )
    valor_plano_atual: float = Field(
        description="Valor do plano de venda antigo.", examples=[99.99]
    )
    nome_plano_sugerido: str = Field(
        description="Nome do plano de venda sugerido.",
        examples=["NEWNET PADRAO - 250MB - 06/2025"],
    )
    valor_plano_sugerido: float = Field(
        description="Valor do plano de venda sugerido.", examples=[99.99]
    )


class PlanoSugeridoListOut(BaseModel):
    data: list[PlanoSugeridoOut] = Field(description="Lista de contratos.")
    meta: misc_schema.Meta
