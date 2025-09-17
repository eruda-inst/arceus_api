from ..enums import StatusAtendimentoCod, StatusAtendimentoRot


STATUS_ATENDIMENTO = {
    StatusAtendimentoCod.NOVO.value: StatusAtendimentoRot.NOVO.value,
    StatusAtendimentoCod.PENDENTE.value: StatusAtendimentoRot.PENDENTE.value,
    StatusAtendimentoCod.EM_PROGRESSO.value: StatusAtendimentoRot.EM_PROGRESSO.value,
    StatusAtendimentoCod.SOLUCIONADO.value: StatusAtendimentoRot.SOLUCIONADO.value,
    StatusAtendimentoCod.CANCELADO.value: StatusAtendimentoRot.CANCELADO.value
}