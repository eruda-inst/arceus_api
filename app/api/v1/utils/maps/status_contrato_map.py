from typing import Dict
from .. import enums


STATUS_CONTRATO: Dict[enums.StatusContratoCod, enums.StatusContratoRot] = {
    enums.StatusContratoCod.PRE_CONTRATO: enums.StatusContratoRot.PRE_CONTRATO,
    enums.StatusContratoCod.ATIVO: enums.StatusContratoRot.ATIVO,
    enums.StatusContratoCod.INATIVO: enums.StatusContratoRot.INATIVO,
    enums.StatusContratoCod.NEGATIVADO: enums.StatusContratoRot.NEGATIVADO,
    enums.StatusContratoCod.DESISTIU: enums.StatusContratoRot.DESISTIU,
}
