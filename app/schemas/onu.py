from pydantic import BaseModel, Field


class StatusONU(BaseModel):
    status_onu: str = Field(description="Sinal de recepção da ONU.")

class StatusONUOut(BaseModel):
    data: StatusONU