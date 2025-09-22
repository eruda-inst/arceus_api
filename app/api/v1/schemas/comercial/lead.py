from typing import Optional, Union
from pydantic import BaseModel, Field


class LeadIn(BaseModel):
    # Campos obrigatórios
    nome: str = Field(max_length=200, description="Nome do lead.")
    id_filial: int = Field(ge=1, description="ID da filial associada ao lead.")
    data_cadastro: Optional[str] = Field(
        default="N/A", max_length=20, description="Data de cadastro do lead."
    )
    fone_celular: str = Field(max_length=20, description="Número do celular do lead.")

    # Campos opcionais
    cep: str = Field(max_length=20, description="CEP do lead.")
    endereco: str = Field(max_length=200, description="Endereço do lead.")
    numero: Optional[Union[str, int]] = Field(
        default="S/N", description="Número da casa do lead."
    )
    bairro: str = Field(max_length=200, description="Bairro do lead.")
    cnpj_cpf: str = Field(max_length=30, description="CNPJ ou CPF do lead.")


class LeadCreate(BaseModel):
    id: int = Field(ge=1, description="ID do lead criado.")
