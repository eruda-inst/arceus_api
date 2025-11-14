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

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"total": 1, "page": 1, "per_page": 10},
                {"total": 1, "page": 2, "per_page": 10},
            ]
        }
    }


class MensagemOut(BaseModel):
    mensagem: str = Field(description="Mensagem de sucesso.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"mensagem": "Operação realizada com sucesso."},
                {"mensagem": "Operação falhou."},
            ]
        }
    }
