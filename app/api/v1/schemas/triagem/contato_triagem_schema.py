from pydantic import BaseModel, Field


class ContatoUpdate(BaseModel):
    telefone_celular: str = Field(
        description="Número do celular do cliente.", examples=["(12) 93456-7890"]
    )


class ContatoOut(BaseModel):
    telefone_celular: str = Field(
        description="Número do celular do cliente.", examples=["(12) 93456-7890"]
    )
