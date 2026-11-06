from pydantic import BaseModel, Field, computed_field

from .. import utils


class OnuStatusOutSchema(BaseModel):
    sinal_rx: float = Field(description="Sinal RX do dispositivo", examples=[-12.34])

    @computed_field(
        description="Status da ONU", examples=[utils.OnuStatusLabel.EXCELLENT]
    )
    @property
    def status_onu(self) -> utils.OnuStatusLabel:
        if self.sinal_rx == 0:
            return utils.OnuStatusLabel.NO_STATUS  # 0 --- Sem status

        if self.sinal_rx >= -8:  # Infinity --- -8.00: satured
            return utils.OnuStatusLabel.SATURATED
        elif self.sinal_rx >= -21:  # -8.01 --- -21.00: excellent
            return utils.OnuStatusLabel.EXCELLENT
        elif self.sinal_rx >= -26:  # -21.01 --- -26.00: good
            return utils.OnuStatusLabel.GOOD
        elif self.sinal_rx >= -31:  # -26.01 --- -31.00: poor
            return utils.OnuStatusLabel.POOR
        else:  # -31.01 --- -Infinity: very poor
            return utils.OnuStatusLabel.VERY_POOR
