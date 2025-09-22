from ..utils import StatusONURot
from pydantic import BaseModel, Field


class StatusONU(BaseModel):
    status_onu: StatusONURot = Field(
        description="Sinal de recepção da ONU.",
    )


class StatusONUOut(BaseModel):
    data: StatusONU
