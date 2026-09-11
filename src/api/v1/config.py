from typing import ClassVar

from pydantic import EmailStr, Field, NonNegativeInt, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    seven_az_api_key: SecretStr = Field(default=SecretStr("seven_az_api_key"))
    seven_az_base_api_url: str = Field(default="http://example.com")

    ixc_access_token: SecretStr = Field(default=SecretStr("ixc_access_token"))
    ixc_base_api_url: str = Field(default="http://example.com")

    opa_access_token: SecretStr = Field(default=SecretStr("opa_access_token"))
    opa_base_api_url: str = Field(default="http://example.com")

    ixc_acs_base_api_url: str = Field(default="http://example.com")
    ixc_acs_client_id: str = Field(default="client_id")
    ixc_acs_client_secret: SecretStr = Field(default=SecretStr("client_secret"))

    db_url_sync: str = Field(default="driver://user:pass@localhost/dbname")
    db_url_async: str = Field(default="driver://user:pass@localhost/dbname")

    dflt_user_email: EmailStr = Field(default="email@email.com")
    dflt_user_name: str = Field(default="dflt_user_name")
    dflt_user_pass: SecretStr = Field(default=SecretStr("dflt_user_pass"))

    pg_db: str = Field(default="pg_db")
    pg_pass: SecretStr = Field(default=SecretStr("pg_pass"))
    pg_user: str = Field(default="pg_user")

    bot_pass: SecretStr = Field(default=SecretStr("bot_pass"))
    bot_username: str = Field(default="bot_username")

    token_expire_minutes: NonNegativeInt = Field(default=0)
    refresh_token_expire_days: NonNegativeInt = Field(default=0)

    secret_key: SecretStr = Field(default=SecretStr("secret_key"))

    run_migrations: str = Field(default="run_migrations")

    @computed_field
    @property
    def token_expire_seconds(self) -> NonNegativeInt:
        return self.token_expire_minutes * 60


settings = Settings()
