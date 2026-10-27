from pydantic import BaseModel, Field, field_serializer

from .. import utils


class OnuStatusOutSchema(BaseModel):
    status_onu: float = Field(
        description="Status da ONU",
        examples=[utils.OnuStatusLabel.EXCELLENT],
    )

    @field_serializer("status_onu")
    def serialize_status_onu(self, v: float) -> utils.OnuStatusLabel:
        if v == 0:
            return utils.OnuStatusLabel.NO_STATUS  # 0 --- Sem status

        if v >= -8:  # Infinity --- -8.00: satured
            return utils.OnuStatusLabel.SATURATED
        elif v >= -21:  # -8.01 --- -21.00: excellent
            return utils.OnuStatusLabel.EXCELLENT
        elif v >= -26:  # -21.01 --- -26.00: good
            return utils.OnuStatusLabel.GOOD
        elif v >= -31:  # -26.01 --- -31.00: poor
            return utils.OnuStatusLabel.POOR
        else:  # -31.01 --- -Infinity: very poor
            return utils.OnuStatusLabel.VERY_POOR
