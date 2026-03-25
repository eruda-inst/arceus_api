from pydantic import BaseModel, Field


class IPUpdate(BaseModel):
    ip: str = Field(description="IP do cliente.", examples=["192.168.1.1"])
