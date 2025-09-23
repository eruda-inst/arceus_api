from typing import Optional, Union
from pydantic import BaseModel, Field
from app.api.v1.utils import Default


class LeadIn(BaseModel):
    nome: str = Field(max_length=200, description="Nome do lead.")
    id_filial: int = Field(ge=1, description="ID da filial associada ao lead.")
    fone_celular: str = Field(max_length=20, description="Número do celular do lead.")
    cep: str = Field(max_length=20, description="CEP do lead.")
    endereco: str = Field(max_length=200, description="Endereço do lead.")
    numero: Optional[Union[str, int]] = Field(
        default="S/N", description="Número da casa do lead."
    )
    bairro: str = Field(max_length=200, description="Bairro do lead.")
    cnpj_cpf: str = Field(max_length=30, description="CNPJ ou CPF do lead.")
    data_cadastro: Optional[str] = Field(
        default="N/A", max_length=20, description="Data de cadastro do lead."
    )
    id_vd_contrato: Optional[int] = Field(
        Default.ID_VD_CONTRATO,
        ge=1,
        description="ID do plano de contrato associado ao lead.",
    )
    id_responsavel: Optional[int] = Field(
        Default.ID_RESPONSAVEL_ARCEUS,
        ge=1,
        description="ID do responsável técnico associado ao lead.",
    )
    cidade: Optional[int] = Field(
        Default.ID_CIDADE_JACOBINA, ge=1, description="ID da cidade associada ao lead."
    )


class LeadCreate(BaseModel):
    id: int = Field(ge=1, description="ID do lead criado.")
