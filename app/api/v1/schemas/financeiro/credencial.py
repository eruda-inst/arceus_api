from pydantic import BaseModel, Field


class CredencialBase(BaseModel):
    senha: str = Field(
        description="Senha da central de acesso do assinante, a ser atualizada.",
    )


class CredencialUpdate(CredencialBase):
    pass


class CredencialOut(CredencialBase):
    pass
