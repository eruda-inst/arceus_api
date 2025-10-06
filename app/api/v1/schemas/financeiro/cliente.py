from pydantic import BaseModel, Field


class CredenciaisBase(BaseModel):
    usuario: str = Field(description="Usuário de acesso à central do assinante.")
    senha: str = Field(description="Senha de acesso à central do assinante.")


class CredenciaisOut(CredenciaisBase):
    pass
