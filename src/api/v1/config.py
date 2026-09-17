"""
Application settings loaded from environment variables / .env file.

Uses Pydantic Settings for validation and typed access.
"""

from typing import ClassVar

from pydantic import EmailStr, Field, NonNegativeInt, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration.

    All fields are loaded from environment variables or a local `.env` file.
    Secret values use `SecretStr` to avoid accidental logging.
    """

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    # SevenAZ API configuration
    seven_az_api_key: SecretStr = Field(default=SecretStr("seven_az_api_key"))
    seven_az_base_api_url: str = Field(default="http://example.com")

    # IXC API configuration
    ixc_access_token: SecretStr = Field(default=SecretStr("ixc_access_token"))
    ixc_base_api_url: str = Field(default="http://example.com")

    # OPA API configuration
    opa_access_token: SecretStr = Field(default=SecretStr("opa_access_token"))
    opa_base_api_url: str = Field(default="http://example.com")

    # IXC ACS (OAuth) configuration
    ixc_acs_base_api_url: str = Field(default="http://example.com")
    ixc_acs_client_id: str = Field(default="client_id")
    ixc_acs_client_secret: SecretStr = Field(default=SecretStr("client_secret"))

    # Database URLs (sync for migrations, async for the app)
    db_url_sync: str = Field(default="driver://user:pass@localhost/dbname")
    db_url_async: str = Field(default="driver://user:pass@localhost/dbname")

    # Default user (used for seeding/bootstrap)
    dflt_user_email: EmailStr = Field(default="email@email.com")
    dflt_user_name: str = Field(default="dflt_user_name")
    dflt_user_pass: SecretStr = Field(default=SecretStr("dflt_user_pass"))

    # Postgres credentials (used for migrations/scripts)
    pg_db: str = Field(default="pg_db")
    pg_pass: SecretStr = Field(default=SecretStr("pg_pass"))
    pg_user: str = Field(default="pg_user")

    # Bot (Basic Auth) credentials
    bot_pass: SecretStr = Field(default=SecretStr("bot_pass"))
    bot_username: str = Field(default="bot_username")

    # JWT token lifetimes
    token_expire_minutes: NonNegativeInt = Field(default=0)
    refresh_token_expire_days: NonNegativeInt = Field(default=0)

    # JWT signing secret
    secret_key: SecretStr = Field(default=SecretStr("secret_key"))

    # Flag controlling whether migrations should run at startup
    run_migrations: str = Field(default="run_migrations")

    # Application timezone
    timezone: str = Field(default="timezone")

    @computed_field
    @property
    def token_expire_seconds(self) -> NonNegativeInt:
        """
        Access token lifetime expressed in seconds.

        Computed from `token_expire_minutes`.

        Returns:
            Token expiry in seconds.
        """
        return self.token_expire_minutes * 60


settings = Settings()
