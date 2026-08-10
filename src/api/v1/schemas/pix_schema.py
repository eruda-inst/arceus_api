from pydantic import BaseModel, Field


class ChavePixOutSchema(BaseModel):
    chave_pix: str = Field(description="Chave pix", examples=["000..."])
