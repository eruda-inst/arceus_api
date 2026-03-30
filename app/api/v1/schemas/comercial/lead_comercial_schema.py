from app.api.v1 import utils
from typing import Optional, Union
from pydantic import BaseModel, Field, PositiveInt


class LeadIn(BaseModel):
    nome: str = Field(max_length=200, description="Nome do lead.", examples=["Joaquim"])
    id_filial: PositiveInt = Field(
        description="ID da filial associada ao lead.", examples=[1]
    )
    fone_celular: str = Field(
        max_length=20,
        description="Número do celular do lead.",
        examples=["(12) 93456-7890"],
    )
    cep: str = Field(max_length=20, description="CEP do lead.", examples=["12345-678"])
    endereco: str = Field(
        max_length=200, description="Endereço do lead.", examples=["Rua do Lead"]
    )
    numero: Optional[Union[str, PositiveInt]] = Field(
        default="S/N", description="Número da casa do lead.", examples=["123"]
    )
    bairro: str = Field(
        max_length=200, description="Bairro do lead.", examples=["Bairro do Lead"]
    )
    cnpj_cpf: str = Field(
        max_length=30, description="CNPJ ou CPF do lead.", examples=["123.456.789-00"]
    )
    data_cadastro: Optional[str] = Field(
        default="N/A",
        max_length=20,
        description="Data de cadastro do lead.",
        examples=["2023-01-01"],
    )
    id_vd_contrato: Optional[PositiveInt] = Field(
        utils.Default.ID_VD_CONTRATO,
        description="ID do plano de contrato associado ao lead.",
        examples=[1],
    )
    id_responsavel: Optional[PositiveInt] = Field(
        utils.Default.ID_RESPONSAVEL_ARCEUS,
        description="ID do responsável técnico associado ao lead.",
        examples=[1],
    )
    cidade: Optional[PositiveInt] = Field(
        utils.Default.ID_CIDADE_JACOBINA,
        description="ID da cidade associada ao lead.",
        examples=[998],
    )


class LeadCreate(BaseModel):
    id: PositiveInt = Field(description="ID do lead criado.", examples=[12345])
