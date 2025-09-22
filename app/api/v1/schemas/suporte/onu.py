from pydantic import BaseModel, Field
from app.api.v1.utils import StatusONURot


class StatusONU(BaseModel):
    status_onu: StatusONURot = Field(
        description="Sinal de recepção da ONU.",
    )


class StatusONUOut(BaseModel):
    data: StatusONU
