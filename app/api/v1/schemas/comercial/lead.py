from app.api.v1 import utils
from typing import Optional, Union
from pydantic import BaseModel, Field, PositiveInt


class LeadIn(BaseModel):
    nome: str = Field(max_length=200, description="Nome do lead.")
    id_filial: PositiveInt = Field(description="ID da filial associada ao lead.")
    fone_celular: str = Field(max_length=20, description="Número do celular do lead.")
    cep: str = Field(max_length=20, description="CEP do lead.")
    endereco: str = Field(max_length=200, description="Endereço do lead.")
    numero: Optional[Union[str, PositiveInt]] = Field(
        default="S/N", description="Número da casa do lead."
    )
    bairro: str = Field(max_length=200, description="Bairro do lead.")
    cnpj_cpf: str = Field(max_length=30, description="CNPJ ou CPF do lead.")
    data_cadastro: Optional[str] = Field(
        default="N/A", max_length=20, description="Data de cadastro do lead."
    )
    id_vd_contrato: Optional[PositiveInt] = Field(
        utils.Default.ID_VD_CONTRATO,
        description="ID do plano de contrato associado ao lead.",
    )
    id_responsavel: Optional[PositiveInt] = Field(
        utils.Default.ID_RESPONSAVEL_ARCEUS,
        description="ID do responsável técnico associado ao lead.",
    )
    cidade: Optional[PositiveInt] = Field(
        utils.Default.ID_CIDADE_JACOBINA, description="ID da cidade associada ao lead."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "nome": "John Doe",
                "id_filial": 1,
                "fone_celular": "+11 (11) 11111-1111",
                "cep": "12345-678",
                "endereco": "Rua Exemplo",
                "numero": "123",
                "bairro": "Bairro Exemplo",
                "cnpj_cpf": "111.111.111-11",
                "data_cadastro": "2023-01-01",
                "id_vd_contrato": 123,
                "id_responsavel": 456,
                "cidade": 789,
            }
        }
    }


class LeadCreate(BaseModel):
    id: PositiveInt = Field(description="ID do lead criado.")

    model_config = {"json_schema_extra": {"example": {"id": 12345}}}
