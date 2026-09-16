from pydantic import BaseModel, Field


class DnsServerOut(BaseModel):
    dns_server: str = Field(
        description="Servidor DNS do dispositivo", examples=["127.0.0.1,1.2.3.4"]
    )


class TemIPV6OutSchema(BaseModel):
    tem_ipv6: bool = Field(
        description="Representa se o cliente tem IPV6 ou não", examples=[True]
    )


class UptimeOutSchema(BaseModel):
    uptime: str = Field(
        description="Uptime do dispositivo em dias, horas, minutos e segundos",
        examples=["01D 02H 03M 04S"],
    )
