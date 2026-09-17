"""
Type definitions for IXC API interactions.
"""

from enum import StrEnum

from pydantic import BaseModel, Field, field_serializer


class SortOrder(StrEnum):
    """
    Sort order for IXC API requests.
    """

    ASC = "asc"
    DESC = "desc"


class Param(BaseModel):
    """
    Represents a single filter parameter for IXC API grid queries.

    Attributes:
        TB: Table and column reference (e.g., "cliente.id").
        OP: Comparison operator (default "=").
        P: Value to compare against (string or integer).
    """

    TB: str = Field()
    OP: str | None = Field(default="=")
    P: str | int = Field()

    @field_serializer("P")
    def serialize_P(self, v: str | int) -> str:
        """
        Serialize the parameter value to a string.

        Args:
            v: The value to serialize.

        Returns:
            The value as a string.
        """
        if isinstance(v, int):
            return str(v)
        return v
