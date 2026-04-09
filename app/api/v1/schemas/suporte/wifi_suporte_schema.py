from pydantic import BaseModel, Field


class WifiOut(BaseModel):
    ssid_wifi_2g: str = Field(description="Nome da rede WiFi 2G", examples=["Rede 2G"])
    senha_wifi_2g: str = Field(
        description="Senha da rede WiFi 2G", examples=["123abcABC"]
    )
    ssid_wifi_5g: str = Field(description="Nome da rede WiFi 5G", examples=["Rede 5G"])
    senha_wifi_5g: str = Field(
        description="Senha da rede WiFi 5G", examples=["123abcABC"]
    )
