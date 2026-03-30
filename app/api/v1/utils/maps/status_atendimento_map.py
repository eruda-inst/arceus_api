from .. import enums
from typing import Dict


STATUS_ATENDIMENTO: Dict[enums.StatusAtendimentoCod, enums.StatusAtendimentoRot] = {
    enums.StatusAtendimentoCod.NOVO: enums.StatusAtendimentoRot.NOVO,
    enums.StatusAtendimentoCod.PENDENTE: enums.StatusAtendimentoRot.PENDENTE,
    enums.StatusAtendimentoCod.EM_PROGRESSO: enums.StatusAtendimentoRot.EM_PROGRESSO,
    enums.StatusAtendimentoCod.SOLUCIONADO: enums.StatusAtendimentoRot.SOLUCIONADO,
    enums.StatusAtendimentoCod.CANCELADO: enums.StatusAtendimentoRot.CANCELADO,
}
