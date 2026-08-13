from pydantic import BaseModel, Field, field_serializer

from .. import utils


class ContatoOutSchema(BaseModel):
    telefone_celular: str = Field(
        description="Celular do cliente",
        min_length=11,  # 12934567890
        max_length=15,  # (12) 93456-7890
        examples=["(12) 93456-7890"],
    )

    @field_serializer("telefone_celular")
    def serialize_telefone_celular(self, v: str) -> str:
        return utils.Formatter.cell(cell=v)


class CredencialOutSchema(BaseModel):
    senha: str = Field(
        description="Senha da central do assinante", examples=["12345678"]
    )
    usuario: str = Field(
        description="Usuário da central do assinante", examples=["usuario"]
    )
