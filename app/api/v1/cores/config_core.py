from pydantic import field_validator, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    OPA_TOKEN: str = ""
    IXC_TOKEN: str = ""
    OPA_HOST: str = ""
    IXC_HOST: str = ""
    API_KEY_7AZ: str = ""
    BASE_URL_7AZ: str = ""

    DB_URL: str = ""
    MIGRATE_DB_URL: str = ""

    SECRET_KEY: SecretStr = SecretStr("")

    @field_validator("DB_URL")
    def change_db_schema(cls, v: str) -> str:
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v


settings = Settings()
