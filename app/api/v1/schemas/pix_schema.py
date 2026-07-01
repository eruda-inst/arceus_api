from pydantic import BaseModel, Field


class ChavePixOut(BaseModel):
    chave_pix: str = Field(
        description="Chave pix.", examples=["00020101021226850014br..."]
    )
