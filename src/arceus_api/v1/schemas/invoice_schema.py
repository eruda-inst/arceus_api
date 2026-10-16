"""
Pydantic schemas for invoice-related responses.
"""

from pydantic import BaseModel, Field, NonNegativeInt, field_serializer

from .. import utils


class DigitableLineOutSchema(BaseModel):
    """
    Response schema for a digitable line (barcode) of an invoice.
    """

    linha_digitavel: str = Field(
        min_length=47,
        max_length=47,
        description="Linha digitável",
        examples=["123..."],
    )


class InvoiceOutSchema(BaseModel):
    """
    Response schema for invoice details.
    """

    id: NonNegativeInt = Field(description="ID da fatura", examples=[1])
    data_vencimento: str = Field(
        description="Data de vencimento da fatura",
        # We can't put this, because IXC
        # min_length=10,  # DD/MM/AAAA
        # max_length=10,  # DD/MM/AAAA
        examples=["DD/MM/AAAA"],
    )
    preco: float = Field(ge=0, description="Preço da fatura", examples=[12.34])
    id_contrato: NonNegativeInt = Field(description="ID do contrato", examples=[12])
    contrato: str = Field(description="Nome do plano", examples=["Nome do plano"])

    @field_serializer("data_vencimento")
    def serialize_data_vencimento(self, v: str) -> str:
        return utils.Formatter.date(date=v)
