from pydantic import BaseModel, Field


class Contato(BaseModel):
    telefone_celular: str = Field(description="Número do celular do cliente.")


class ContatoUpdate(Contato):
    model_config = {
        "json_schema_extra": {
            "example": {
                "telefone_celular": "(12) 93456-7890",
            }
        }
    }


class ContatoOut(Contato):
    model_config = {
        "json_schema_extra": {
            "example": {
                "telefone_celular": "(12) 93456-7890",
            }
        }
    }
