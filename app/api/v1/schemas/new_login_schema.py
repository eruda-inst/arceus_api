from .. import utils
from pydantic import BaseModel, field_serializer, Field


class StatusConexaoOut(BaseModel):
    status_conexao: utils.StatusConexaoCod = Field(
        description="Status da conexão.", examples=[utils.StatusConexaoRot.CONECTADO]
    )

    @field_serializer("status_conexao")
    def serialize_status_conexao(self, v: utils.StatusConexaoCod):
        Cod = utils.StatusConexaoCod
        Rot = utils.StatusConexaoRot

        mapping = {
            Cod.CONECTADO: Rot.CONECTADO,
            Cod.DESCONECTADO: Rot.DESCONECTADO,
            Cod.SEM_STATUS: Rot.SEM_STATUS,
        }

        return mapping[v]


class WifiOut(BaseModel):
    ssid_wifi_2g: str = Field(description="Nome da rede WiFi 2G", examples=["Rede 2G"])
    senha_wifi_2g: str = Field(
        description="Senha da rede WiFi 2G", examples=["12345678"]
    )
    ssid_wifi_5g: str = Field(description="Nome da rede WiFi 5G", examples=["Rede 5G"])
    senha_wifi_5g: str = Field(
        description="Senha da rede WiFi 5G", examples=["12345678"]
    )
