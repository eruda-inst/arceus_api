from ..enums import StatusConexaoCod, StatusConexaoRot


STATUS_CONEXAO = {
    StatusConexaoCod.CONECTADO.value: StatusConexaoRot.CONECTADO.value,
    StatusConexaoCod.SEM_STATUS.value: StatusConexaoRot.SEM_STATUS.value,
    StatusConexaoCod.DESCONECTADO.value: StatusConexaoRot.DESCONECTADO.value
}