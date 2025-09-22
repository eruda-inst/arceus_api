from ..enums import StatusConexaoCod, StatusConexaoRot


STATUS_CONEXAO = {
    StatusConexaoCod.CONECTADO: StatusConexaoRot.CONECTADO,
    StatusConexaoCod.SEM_STATUS: StatusConexaoRot.SEM_STATUS,
    StatusConexaoCod.DESCONECTADO: StatusConexaoRot.DESCONECTADO,
}
