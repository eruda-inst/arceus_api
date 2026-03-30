from .. import enums
from typing import Dict


STATUS_ACESSO: Dict[enums.StatusAcessoCod, enums.StatusAcessoRot] = {
    enums.StatusAcessoCod.AGUARDANDO_ASSINATURA: enums.StatusAcessoRot.AGUARDANDO_ASSINATURA,
    enums.StatusAcessoCod.ATIVO: enums.StatusAcessoRot.ATIVO,
    enums.StatusAcessoCod.BLOQUEIO_AUTOMATICO: enums.StatusAcessoRot.BLOQUEIO_AUTOMATICO,
    enums.StatusAcessoCod.BLOQUEIO_MANUAL: enums.StatusAcessoRot.BLOQUEIO_MANUAL,
    enums.StatusAcessoCod.DESATIVADO: enums.StatusAcessoRot.DESATIVADO,
    enums.StatusAcessoCod.FINANCEIRO_EM_ATRASO: enums.StatusAcessoRot.FINANCEIRO_EM_ATRASO,
}
