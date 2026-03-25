from pydantic import BaseModel, Field


class Contato(BaseModel):
    telefone_celular: str = Field(
        description="Número do celular do cliente.", examples=["(12) 93456-7890"]
    )


class ContatoUpdate(Contato):
    pass


class ContatoOut(Contato):
    pass
