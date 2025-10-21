from pydantic import BaseModel, Field


class CredencialUpdate(BaseModel):
    senha: str = Field(
        description="Senha da central de acesso do assinante, a ser atualizada."
    )

    model_config = {"json_schema_extra": {"example": {"senha": "12345678"}}}


class CredencialBase(CredencialUpdate):
    usuario: str = Field(
        description="Usuário da central de acesso do assinante, a ser atualizado."
    )

    model_config = {
        "json_schema_extra": {
            "example": {"usuario": "12312312312", "senha": "12345678"}
        }
    }


class CredencialOut(CredencialBase):
    pass
