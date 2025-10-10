from pydantic import BaseModel, Field


class ContatoUpdate(BaseModel):
    telefone_celular: str = Field(description="Número do celular a ser atualizado.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "telefone_celular": "12 93456 7890",
                }
            ]
        }
    }
