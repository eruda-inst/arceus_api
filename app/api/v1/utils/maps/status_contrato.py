from ..enums import StatusContratoCod, StatusContratoRot


STATUS_CONTRATO = {
    StatusContratoCod.PRE_CONTRATO: StatusContratoRot.PRE_CONTRATO,
    StatusContratoCod.ATIVO: StatusContratoRot.ATIVO,
    StatusContratoCod.INATIVO: StatusContratoRot.INATIVO,
    StatusContratoCod.NEGATIVADO: StatusContratoRot.NEGATIVADO,
    StatusContratoCod.DESISTIU: StatusContratoRot.DESISTIU
}