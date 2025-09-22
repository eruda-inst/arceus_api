from ..enums import StatusAtendimentoCod, StatusAtendimentoRot


STATUS_ATENDIMENTO = {
    StatusAtendimentoCod.NOVO: StatusAtendimentoRot.NOVO,
    StatusAtendimentoCod.PENDENTE: StatusAtendimentoRot.PENDENTE,
    StatusAtendimentoCod.EM_PROGRESSO: StatusAtendimentoRot.EM_PROGRESSO,
    StatusAtendimentoCod.SOLUCIONADO: StatusAtendimentoRot.SOLUCIONADO,
    StatusAtendimentoCod.CANCELADO: StatusAtendimentoRot.CANCELADO,
}
