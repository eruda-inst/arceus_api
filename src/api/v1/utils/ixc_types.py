from enum import StrEnum

from pydantic import BaseModel, Field, field_serializer


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class Param(BaseModel):
    TB: str = Field()
    OP: str | None = Field(default="=")
    P: str | int = Field()

    @field_serializer("P")
    def serialize_P(self, v: str | int) -> str:
        if isinstance(v, int):
            return str(v)
        return v
