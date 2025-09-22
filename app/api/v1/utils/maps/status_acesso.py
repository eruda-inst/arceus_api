from ..enums import StatusAcessoRot, StatusAcessoCod


STATUS_ACESSO = {
    StatusAcessoCod.AGUARDANDO_ASSINATURA: StatusAcessoRot.AGUARDANDO_ASSINATURA,
    StatusAcessoCod.ATIVO: StatusAcessoRot.ATIVO,
    StatusAcessoCod.BLOQUEIO_AUTOMATICO: StatusAcessoRot.BLOQUEIO_AUTOMATICO,
    StatusAcessoCod.BLOQUEIO_MANUAL: StatusAcessoRot.BLOQUEIO_MANUAL,
    StatusAcessoCod.DESATIVADO: StatusAcessoRot.DESATIVADO,
    StatusAcessoCod.FINANCEIRO_EM_ATRASO: StatusAcessoRot.FINANCEIRO_EM_ATRASO,
}
