from pydantic import BaseModel, Field


class DnsServerOut(BaseModel):
    dns_server: str = Field(
        description="Servidor DNS do dispositivo", examples=["127.0.0.1,1.2.3.4"]
    )


class HasIPV6OutSchema(BaseModel):
    tem_ipv6: bool = Field(
        description="Representa se o cliente tem IPV6 ou não", examples=[True]
    )


class UptimeOutSchema(BaseModel):
    uptime: str = Field(
        description="Uptime do dispositivo em dias, horas, minutos e segundos",
        examples=["01D 02H 03M 04S"],
    )


class FiberSignalOutSchema(BaseModel):
    rx: float = Field(description="Taxa de recepção do sinal da fibra", examples=[1.23])
    tx: float = Field(
        description="Taxa de transmissão do sinal da fibra", examples=[4.56]
    )
