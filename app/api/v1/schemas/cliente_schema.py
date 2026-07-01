from pydantic import BaseModel, Field


class ContatoOut(BaseModel):
    telefone_celular: str = Field(
        description="Número do celular do cliente.", examples=["(12) 93456-7890"]
    )


class ClienteExisteOut(BaseModel):
    cliente_existe: bool = Field(description="Indica se o cliente existe no Opa.")


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
