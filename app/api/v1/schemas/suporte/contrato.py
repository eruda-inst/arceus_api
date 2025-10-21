from .. import misc
from typing import List
from app.api.v1 import utils
from pydantic import BaseModel, Field, PositiveInt


class Contrato(BaseModel):
    id: PositiveInt = Field(description="ID único do contrato.")
    id_login: PositiveInt = Field(description="ID de login associado ao contrato.")
    id_cliente: PositiveInt = Field(description="ID do cliente associado ao contrato.")
    status: utils.StatusContratoRot = Field(description="Status atual do contrato.")
    contrato: str = Field(max_length=100, description="Número do contrato.")
    valor: float = Field(description="Valor do contrato.")
    data_vencimento: str = Field(description="Data de vencimento do contrato.")
    mac_onu: str = Field(description="MAC Address da ONU.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 123,
                "id_login": 456,
                "id_cliente": 789,
                "status": utils.enums.rotulos.StatusContratoRot.PRE_CONTRATO,
                "contrato": "NEWNET PADRAO - 250MB - 06/2025",
                "valor": 99.99,
                "data_vencimento": "2025-12-31",
                "mac_onu": "AB1230001234",
            }
        }
    }


class ContratoListOut(BaseModel):
    data: List[Contrato] = Field(description="Lista de contratos")
    meta: misc.Meta
    links: misc.Links

    model_config = {
        "json_schema_extra": {
            "example": {
                "data": [
                    {
                        "id": 123,
                        "id_login": 456,
                        "id_cliente": 789,
                        "status": utils.enums.rotulos.StatusContratoRot.PRE_CONTRATO,
                        "contrato": "NEWNET PADRAO - 250MB - 06/2025",
                        "valor": 99.99,
                        "data_vencimento": "2025-12-31",
                        "mac_onu": "AB1230001234",
                    },
                    {
                        "id": 234,
                        "id_login": 567,
                        "id_cliente": 890,
                        "status": utils.enums.rotulos.StatusContratoRot.PRE_CONTRATO,
                        "contrato": "NEWNET PADRAO - 250MB - 06/2025",
                        "valor": 99.99,
                        "data_vencimento": "2025-12-31",
                        "mac_onu": "BC2341112345",
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
                    "self": "/api/v1/suporte/contratos?protocolo=NWT202537245&page=1&per_page=10",
                },
            }
        }
    }
