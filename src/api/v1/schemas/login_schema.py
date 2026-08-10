from pydantic import BaseModel, Field, PositiveInt, field_serializer

from .. import utils


class IpOutSchema(BaseModel):
    ip: str = Field(description="IP do login", examples=["123.456.7.890"])
    pool_radius: PositiveInt = Field(
        ge=1, description="Pool Radius do login", examples=[1]
    )


class StatusConexaoOutSchema(BaseModel):
    status_conexao: utils.StatusConexaoCod = Field(
        description="Status da conexão", examples=[utils.StatusConexaoRot.CONECTADO]
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


class WifiOutSchema(BaseModel):
    ssid_wifi_2g: str | None = Field(
        default=None, description="Nome da rede WiFi 2G", examples=["Rede 2G"]
    )
    senha_wifi_2g: str | None = Field(
        default=None, description="Senha da rede WiFi 2G", examples=["12345678"]
    )
    ssid_wifi_5g: str | None = Field(
        default=None, description="Nome da rede WiFi 5G", examples=["Rede 5G"]
    )
    senha_wifi_5g: str | None = Field(
        default=None, description="Senha da rede WiFi 5G", examples=["12345678"]
    )
