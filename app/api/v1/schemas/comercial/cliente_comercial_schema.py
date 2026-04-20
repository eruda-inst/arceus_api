from pydantic import BaseModel, Field


class ClienteExisteOut(BaseModel):
    cliente_existe: bool = Field(description="Indica se o cliente existe no Opa.")
