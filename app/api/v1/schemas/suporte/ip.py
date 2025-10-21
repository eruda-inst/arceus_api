from pydantic import BaseModel, Field


class IPUpdate(BaseModel):
    ip: str = Field(description="IP do cliente.")

    model_config = {"json_schema_extra": {"example": {"ip": "192.168.1.1"}}}
