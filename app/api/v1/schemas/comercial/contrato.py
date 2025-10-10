from .. import misc
from typing import List
from app.api.v1 import utils
from pydantic import BaseModel, Field, PositiveInt


class Contrato(BaseModel):
    id: PositiveInt = Field(description="ID único do contrato.")
    contrato: str = Field(max_length=100, description="Número do contrato.")
    valor: float = Field(description="Valor do contrato.")
    status_acesso: utils.StatusAcessoRot = Field(
        description="Status do acesso do contrato."
    )
    data_vencimento: str = Field(description="Data de vencimento do contrato.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "data": [
                        {
                            "id": 1234,
                            "contrato": "NEWNET PADRAO - 250MB - 06/2025",
                            "valor": 99.99,
                            "status_acesso": utils.enums.rotulos.status_acesso.StatusAcessoRot.ATIVO,
                            "data_vencimento": "2025-12-31",
                        },
                    ],
                }
            ]
        }
    }


class ContratoListOut(BaseModel):
    data: List[Contrato] = Field(description="Lista de contratos")
    meta: misc.Meta
    links: misc.Links

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "data": [
                        {
                            "id": 1234,
                            "contrato": "NEWNET PADRAO - 250MB - 06/2025",
                            "valor": 99.99,
                            "status_acesso": utils.enums.rotulos.status_acesso.StatusAcessoRot.ATIVO,
                            "data_vencimento": "2025-12-31",
                        },
                        {
                            "id": 12345,
                            "contrato": "Newnet 2024 - 350MB",
                            "valor": 99.9,
                            "status_acesso": utils.enums.rotulos.status_acesso.StatusAcessoRot.ATIVO,
                            "data_vencimento": "2025-12-31",
                        },
                    ],
                    "meta": {
                        "total": 2,
                        "page": 1,
                        "per_page": 10,
                    },
                    "links": {
                        "next": "null",
                        "prev": "null",
                        "self": "/api/v1/comercial/contratos?protocolo=NWT202537591&page=1&per_page=10",
                    },
                }
            ]
        }
    }
