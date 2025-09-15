from pydantic import BaseModel, Field


class StatusONU(BaseModel):
    sinal_rx: float = Field(description="Sinal de recepção da ONU.")
    sinal_tx: float = Field(description="Sinal de transmissão da ONU.")

class StatusONUOut(BaseModel):
    data: StatusONU