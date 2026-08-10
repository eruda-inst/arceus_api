from pydantic import BaseModel, Field, field_serializer

from .. import utils


class StatusOnuOutSchema(BaseModel):
    status_onu: float = Field(
        description="Status da ONU",
        examples=[utils.StatusOnuRot.EXCELENTE],
    )

    @field_serializer("status_onu")
    def serialize_status_onu(self, v: float) -> utils.StatusOnuRot:
        if v >= -15:
            return utils.StatusOnuRot.SATURADO
        elif v >= -21:
            return utils.StatusOnuRot.EXCELENTE
        elif v >= -26:
            return utils.StatusOnuRot.BOM
        elif v >= -29:
            return utils.StatusOnuRot.REGULAR
        elif v >= -31:
            return utils.StatusOnuRot.RUIM
        else:
            return utils.StatusOnuRot.PESSIMO
