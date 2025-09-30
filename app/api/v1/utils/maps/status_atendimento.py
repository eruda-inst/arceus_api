from typing import Dict
from ..enums import StatusAtendimentoCod, StatusAtendimentoRot


STATUS_ATENDIMENTO: Dict[StatusAtendimentoCod, StatusAtendimentoRot] = {
    StatusAtendimentoCod.NOVO: StatusAtendimentoRot.NOVO,
    StatusAtendimentoCod.PENDENTE: StatusAtendimentoRot.PENDENTE,
    StatusAtendimentoCod.EM_PROGRESSO: StatusAtendimentoRot.EM_PROGRESSO,
    StatusAtendimentoCod.SOLUCIONADO: StatusAtendimentoRot.SOLUCIONADO,
    StatusAtendimentoCod.CANCELADO: StatusAtendimentoRot.CANCELADO,
}
