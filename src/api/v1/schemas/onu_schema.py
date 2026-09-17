from pydantic import BaseModel, Field, field_serializer

from .. import utils


class OnuStatusOutSchema(BaseModel):
    status_onu: float = Field(
        description="Status da ONU",
        examples=[utils.OnuStatusLabel.EXCELLENT],
    )

    @field_serializer("status_onu")
    def serialize_status_onu(self, v: float) -> utils.OnuStatusLabel:
        if v >= -15:
            return utils.OnuStatusLabel.SATURATED
        elif v >= -21:
            return utils.OnuStatusLabel.EXCELLENT
        elif v >= -26:
            return utils.OnuStatusLabel.GOOD
        elif v >= -29:
            return utils.OnuStatusLabel.FAIR
        elif v >= -31:
            return utils.OnuStatusLabel.POOR
        else:
            return utils.OnuStatusLabel.VERY_POOR
