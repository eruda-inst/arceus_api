from typing import Any
from enum import StrEnum
from pydantic import BaseModel, field_serializer, Field


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class Param(BaseModel):
    TB: str = Field()
    OP: str | None = Field(default="=")
    P: Any = Field()

    @field_serializer("P")
    def serialize_P(self, v: Any) -> str:
        if isinstance(v, int):
            return str(v)
        return v
