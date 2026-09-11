from pydantic import BaseModel, Field


class DnsServerOut(BaseModel):
    dns_server: str = Field(
        description="Servidor DNS do dispositivo", examples=["127.0.0.1,1.2.3.4"]
    )
