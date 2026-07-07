from pydantic import field_validator, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    api_key_7az: SecretStr = SecretStr("")
    base_url_7az: str = ""
    db_url: str = ""
    ixc_host: str = ""
    ixc_token: SecretStr = SecretStr("")
    migrate_db_url: str = ""
    opa_host: str = ""
    opa_token: SecretStr = SecretStr("")
    postgres_db: str = ""
    postgres_password: SecretStr = SecretStr("")
    postgres_user: str = ""
    secret_key: SecretStr = SecretStr("")

    @field_validator("db_url")
    def change_db_schema(cls, v: str) -> str:
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v


settings = Settings()
