from .. import enums
from typing import Dict


STATUS_CONEXAO: Dict[enums.StatusConexaoCod, enums.StatusConexaoRot] = {
    enums.StatusConexaoCod.CONECTADO: enums.StatusConexaoRot.CONECTADO,
    enums.StatusConexaoCod.SEM_STATUS: enums.StatusConexaoRot.SEM_STATUS,
    enums.StatusConexaoCod.DESCONECTADO: enums.StatusConexaoRot.DESCONECTADO,
}
