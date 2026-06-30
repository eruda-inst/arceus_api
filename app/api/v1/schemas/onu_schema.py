from .. import utils
from pydantic import BaseModel, field_serializer, Field, NonNegativeFloat


class StatusOnuOut(BaseModel):
    status_onu: NonNegativeFloat = Field(
        description="Status da ONU.", examples=[utils.StatusONURot.EXCELENTE]
    )

    @field_serializer("status_onu")
    def serialize_status_onu(self, v: float):
        if v >= -15:
            return utils.StatusONURot.SATURADO
        elif v >= -21:
            return utils.StatusONURot.EXCELENTE
        elif v >= -26:
            return utils.StatusONURot.BOM
        elif v >= -29:
            return utils.StatusONURot.REGULAR
        elif v >= -31:
            return utils.StatusONURot.RUIM
        else:
            return utils.StatusONURot.PESSIMO
