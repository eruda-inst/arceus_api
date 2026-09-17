# auth_schema.py
"""
Pydantic schemas for authentication.
"""

from pydantic import BaseModel, Field, NonNegativeInt


class AccessTokenOutSchema(BaseModel):
    """
    Response schema for access and refresh tokens.
    """

    access_token: str = Field(description="Token de acesso", examples=["eyJ..."])
    refresh_token: str = Field(description="Token de atualização", examples=["eyJ..."])
    token_type: str | None = Field(
        default="Bearer", description="Tipo de token", examples=["Bearer"]
    )
    expires_in: NonNegativeInt | None = Field(
        default=3600,  # 1h
        description="Tempo de expiração em segundos",
        examples=[3600],
        ge=60,
    )


class RefreshTokenInSchema(BaseModel):
    """
    Input schema for refreshing an access token.
    """

    refresh_token: str = Field(description="Token de atualização", examples=["eyJ..."])
