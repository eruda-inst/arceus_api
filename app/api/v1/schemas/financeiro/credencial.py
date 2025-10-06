from typing import Optional
from pydantic import BaseModel, Field


class CredencialBase(BaseModel):
    usuario: Optional[str] = Field(
        default=None,
        description="Usuário da central de acesso do assinante, a ser atualizado.",
    )
    senha: Optional[str] = Field(
        default=None,
        description="Senha da central de acesso do assinante, a ser atualizada.",
    )


class CredencialUpdate(CredencialBase):
    pass


class CredencialOut(CredencialBase):
    pass
