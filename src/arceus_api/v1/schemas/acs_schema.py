"""
Pydantic schemas for ACS (Automatic Configuration Server) related responses.
"""

from pydantic import BaseModel, Field


class DnsServerOut(BaseModel):
    """
    Response schema for DNS server information.
    """

    dns_server: str = Field(
        description="Servidor DNS do dispositivo", examples=["127.0.0.1,1.2.3.4"]
    )


class HasIPV6OutSchema(BaseModel):
    """
    Response schema indicating whether the client has IPv6 enabled.
    """

    tem_ipv6: bool = Field(
        description="Representa se o cliente tem IPV6 ou não", examples=[True]
    )


class UptimeOutSchema(BaseModel):
    """
    Response schema for device uptime.
    """

    uptime: str = Field(
        description="Uptime do dispositivo em dias, horas, minutos e segundos",
        examples=["01D 02H 03M 04S"],
    )


class FiberSignalOutSchema(BaseModel):
    """
    Response schema for fiber optic signal levels (RX and TX).
    """

    rx: float = Field(description="Taxa de recepção do sinal da fibra", examples=[1.23])
    tx: float = Field(
        description="Taxa de transmissão do sinal da fibra", examples=[4.56]
    )
