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
            "examples": [
                {
                    "id": 324,
                    "id_login": 133,
                    "id_cliente": 2321,
                    "status": utils.enums.rotulos.StatusContratoRot.PRE_CONTRATO,
                    "contrato": "NEWNET PADRAO - 250MB - 06/2025",
                    "valor": 99.9,
                    "data_vencimento": "2025-06-01",
                    "mac_onu": "DD18b3d3e400",
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
                            "id": 8516,
                            "id_login": 8247,
                            "id_cliente": 7921,
                            "status": utils.enums.rotulos.StatusContratoRot.ATIVO,
                            "contrato": "NEWNET BASICO - 150MB - 06/2025",
                            "valor": 50.0,
                            "data_vencimento": "2025-10-20",
                            "mac_onu": "DD16E6112683",
                        },
                        {
                            "id": 11807,
                            "id_login": 11582,
                            "id_cliente": 7921,
                            "status": utils.enums.rotulos.StatusContratoRot.ATIVO,
                            "contrato": "NEWNET BASICO - 150MB - 06/2025",
                            "valor": 55.0,
                            "data_vencimento": "2025-10-10",
                            "mac_onu": "GPON00a31548",
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
            ]
        }
    }
