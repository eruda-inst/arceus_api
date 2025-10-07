from pydantic import BaseModel, Field


class CredencialBase(BaseModel):
    usuario: str = Field(
        description="Usuário da central de acesso do assinante, a ser atualizado."
    )
    senha: str = Field(
        description="Senha da central de acesso do assinante, a ser atualizada."
    )


class CredencialUpdate(BaseModel):
    senha: str = Field(
        description="Senha da central de acesso do assinante, a ser atualizada."
    )


class CredencialOut(CredencialBase):
    pass
