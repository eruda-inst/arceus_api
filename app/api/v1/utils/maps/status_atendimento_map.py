from .. import enums
from typing import Dict

STATUS_ATENDIMENTO: Dict[enums.SuStatusCod, enums.SuStatusRot] = {
    enums.SuStatusCod.NOVO: enums.SuStatusRot.NOVO,
    enums.SuStatusCod.PENDENTE: enums.SuStatusRot.PENDENTE,
    enums.SuStatusCod.EM_PROGRESSO: enums.SuStatusRot.EM_PROGRESSO,
    enums.SuStatusCod.SOLUCIONADO: enums.SuStatusRot.SOLUCIONADO,
    enums.SuStatusCod.CANCELADO: enums.SuStatusRot.CANCELADO,
}
