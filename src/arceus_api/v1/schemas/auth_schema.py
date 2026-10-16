# auth_schema.py
"""
Pydantic schemas for authentication.
"""

import datetime as dt

from pydantic import BaseModel, Field, NonNegativeInt


class AccessTokenOutSchema(BaseModel):
    """
    Response schema for access and refresh tokens.
    """

    expires_in: NonNegativeInt | None = Field(
        default=3600, description="Tempo de expiração em segundos", examples=[3600]
    )
    expires_at: dt.datetime = Field(
        description="Data prevista para expiração do token",
        examples=["YYYY-MM-DDTHH:MM:SS.ss"],
    )
    token_type: str | None = Field(
        default="Bearer", description="Tipo de token", examples=["Bearer"]
    )
    access_token: str = Field(description="Token de acesso", examples=["eyJ..."])
    refresh_token: str = Field(description="Token de atualização", examples=["eyJ..."])


class RefreshTokenInSchema(BaseModel):
    """
    Input schema for refreshing an access token.
    """

    refresh_token: str = Field(description="Token de atualização", examples=["eyJ..."])
