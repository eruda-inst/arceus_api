from typing import Dict
from ..enums import StatusConexaoCod, StatusConexaoRot


STATUS_CONEXAO: Dict[StatusConexaoCod, StatusConexaoRot] = {
    StatusConexaoCod.CONECTADO: StatusConexaoRot.CONECTADO,
    StatusConexaoCod.SEM_STATUS: StatusConexaoRot.SEM_STATUS,
    StatusConexaoCod.DESCONECTADO: StatusConexaoRot.DESCONECTADO,
}
