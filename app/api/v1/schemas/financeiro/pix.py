from pydantic import BaseModel, Field


class ChavePixBase(BaseModel):
    chave_pix: str = Field(description="Chave pix.")
