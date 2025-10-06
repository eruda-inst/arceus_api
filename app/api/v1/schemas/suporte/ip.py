from pydantic import BaseModel, Field


class IPUpdate(BaseModel):
    ip: str = Field(description="IP do cliente.")
