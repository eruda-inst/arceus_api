from pydantic import BaseModel, Field


class StatusONU(BaseModel):
    sinal_rx: float = Field(default=0.00, description="Sinal de recepção da ONU.")
    sinal_tx: float = Field(default=0.00, description="Sinal de transmissão da ONU.")


class StatusONUOut(BaseModel):
    data: StatusONU