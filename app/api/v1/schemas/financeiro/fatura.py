from .. import misc
from typing import List
from pydantic import BaseModel, Field, PositiveInt, NonNegativeInt, PositiveFloat


class Fatura(BaseModel):
    id: PositiveInt = Field(description="ID da fatura.")
    data_vencimento: str = Field(
        max_length=10, description="Data de vencimento da fatura."
    )
    preco: float = Field(description="Preço da fatura.")

    model_config = {
        "json_schema_extra": {
            "examples": [{"id": 123, "data_vencimento": "2025-12-31", "preco": 99.99}]
        }
    }


class FaturaAberta(Fatura):
    id_contrato: NonNegativeInt = Field(description="ID de contrato associado à fatura")
    contrato: str = Field(description="Nome do contrato associado à fatura.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 123,
                    "data_vencimento": "2025-12-31",
                    "preco": 99.99,
                    "id_contrato": 1234,
                    "contrato": "NEWNET PADRAO - 250MB - 06/2025",
                }
            ]
        }
    }


class FaturaAbertaListOut(BaseModel):
    data: List[FaturaAberta]
    meta: misc.Meta
    links: misc.Links

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "data": [
                        {
                            "id": 123,
                            "data_vencimento": "2025-12-31",
                            "preco": 99.99,
                            "id_contrato": 1234,
                            "contrato": "NEWNET PREMIUM+ - 500MB - 06/2025",
                        },
                        {
                            "id": 124,
                            "data_vencimento": "2025-12-31",
                            "preco": 99.99,
                            "id_contrato": 1234,
                            "contrato": "NEWNET PREMIUM+ - 500MB - 06/2025",
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
                        "self": "/api/v1/financeiro/faturas_abertas?protocolo=NWT202537591&page=1&per_page=10",
                    },
                }
            ]
        }
    }


class LinhaDigitavelBase(BaseModel):
    linha_digitavel: str = Field(
        min_length=47, max_length=47, description="Linha digitável."
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"linha_digitavel": "12345678901234567890123456789012345678901234567"}
            ]
        }
    }


class LinhaDigitavelOut(BaseModel):
    data: LinhaDigitavelBase

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "data": [
                        {
                            "linha_digitavel": "12345678901234567890123456789012345678901234567"
                        }
                    ]
                }
            ]
        }
    }


class FaturaPagaBase(Fatura):
    valor_pago: PositiveFloat = Field(description="Valor pago.")
    data_pagamento: str = Field(
        max_length=10, description="Data de pagamento da fatura."
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 123,
                    "data_vencimento": "2025-12-31",
                    "preco": 99.99,
                    "valor_pago": 99.99,
                    "data_pagamento": "2025-12-31",
                }
            ]
        }
    }
