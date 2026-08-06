from pydantic import EmailStr, Field, NonNegativeInt, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    api_key_7az: SecretStr = Field(default=SecretStr("api_key_7az"))
    base_api_url_7az: str = Field(default="http://exemplo.com")

    ixc_token: SecretStr = Field(default=SecretStr("api_key_ixc"))
    base_api_url_ixc: str = Field(default="http://exemplo.com")

    opa_token: SecretStr = Field(default=SecretStr("base_api_url_opa"))
    base_api_url_opa: str = Field(default="http://exemplo.com")

    db_url_sync: str = Field(default="driver://user:pass@localhost/dbname")
    db_url_async: str = Field(default="driver://user:pass@localhost/dbname")

    dflt_user_email: EmailStr = Field(default="email@email.com")
    dflt_user_name: str = Field(default="default_user_name")
    dflt_user_pass: SecretStr = Field(default=SecretStr("dflt_user_pass"))

    pg_db: str = Field(default="pg_db")
    pg_pass: SecretStr = Field(default=SecretStr("pg_pass"))
    pg_user: str = Field(default="pg_user")

    token_expire_minutes: NonNegativeInt = Field(default=0)
    refresh_token_expire_days: NonNegativeInt = Field(default=0)

    secret_key: SecretStr = Field(default=SecretStr("secret_key"))

    run_migrations: str = Field(default="run_migrations")

    @computed_field
    @property
    def token_expire_seconds(self) -> NonNegativeInt:
        return self.token_expire_minutes * 60


settings = Settings()
