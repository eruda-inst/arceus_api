"""
Pydantic schemas for Pix-related responses.
"""

from pydantic import BaseModel, Field


class PixKeyOutSchema(BaseModel):
    """
    Response schema for a Pix key.
    """

    chave_pix: str = Field(description="Chave pix", examples=["000..."])
