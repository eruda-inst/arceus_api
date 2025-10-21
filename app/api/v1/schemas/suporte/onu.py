from app.api.v1 import utils
from pydantic import BaseModel, Field


class StatusONU(BaseModel):
    status_onu: utils.StatusONURot = Field(description="Sinal de recepção da ONU.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status_onu": utils.StatusONURot.EXCELENTE,
            }
        }
    }


class StatusONUOut(BaseModel):
    data: StatusONU

    model_config = {
        "json_schema_extra": {
            "example": {
                "data": {
                    "status_onu": utils.StatusONURot.EXCELENTE,
                }
            }
        }
    }
