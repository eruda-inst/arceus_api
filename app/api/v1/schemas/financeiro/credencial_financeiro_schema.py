from pydantic import BaseModel, Field


class CredencialUpdate(BaseModel):
    senha: str = Field(
        description="Senha da central de acesso do assinante, a ser atualizada.",
        examples=["12345678"],
    )


class CredencialBase(CredencialUpdate):
    usuario: str = Field(
        description="Usuário da central de acesso do assinante, a ser atualizado.",
        examples=["usuario"],
    )


class CredencialOut(CredencialBase):
    pass
