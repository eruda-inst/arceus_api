from pydantic import BaseModel, Field, NonNegativeInt


class AccessTokenOut(BaseModel):
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


class RefreshTokenIn(BaseModel):
    refresh_token: str = Field(description="Token de atualização", examples=["eyJ..."])
