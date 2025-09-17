from ..enums import StatusContratoCod, StatusContratoRot


STATUS_CONTRATO = {
    StatusContratoCod.PRE_CONTRATO.value: StatusContratoRot.PRE_CONTRATO.value,
    StatusContratoCod.ATIVO.value: StatusContratoRot.ATIVO.value,
    StatusContratoCod.INATIVO.value: StatusContratoRot.INATIVO.value,
    StatusContratoCod.NEGATIVADO.value: StatusContratoRot.NEGATIVADO.value,
    StatusContratoCod.DESISTIU.value: StatusContratoRot.DESISTIU.value
}