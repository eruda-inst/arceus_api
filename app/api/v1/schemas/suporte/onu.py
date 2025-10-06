from app.api.v1 import utils
from pydantic import BaseModel, Field


class StatusONU(BaseModel):
    status_onu: utils.StatusONURot = Field(description="Sinal de recepção da ONU.")


class StatusONUOut(BaseModel):
    data: StatusONU
