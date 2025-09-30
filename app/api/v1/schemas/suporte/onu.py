from pydantic import BaseModel, Field
from app.api.v1 import utils


class StatusONU(BaseModel):
    status_onu: utils.StatusONURot = Field(description="Sinal de recepção da ONU.")


class StatusONUOut(BaseModel):
    data: StatusONU
