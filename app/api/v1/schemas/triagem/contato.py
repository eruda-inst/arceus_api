from pydantic import BaseModel, Field


class ContatoUpdate(BaseModel):
    telefone_celular: str = Field(description="Número do celular a ser atualizado.")
