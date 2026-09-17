from pydantic import BaseModel, Field


class PixKeyOutSchema(BaseModel):
    chave_pix: str = Field(description="Chave pix", examples=["000..."])
