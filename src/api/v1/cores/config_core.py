from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    api_key_7az: SecretStr = SecretStr("")
    base_url_7az: str = ""

    db_url: str = ""
    db_url_migrations: str = ""

    # Não quero por valor padrão aqui, então não pode ser EmailStr, pois ele não aceita ""
    default_user_email: str = ""
    default_user_name: str = ""
    default_user_password: SecretStr = SecretStr("")

    ixc_host: str = ""
    ixc_token: SecretStr = SecretStr("")

    opa_host: str = ""
    opa_token: SecretStr = SecretStr("")

    postgres_db: str = ""
    postgres_password: SecretStr = SecretStr("")
    postgres_user: str = ""

    secret_key: SecretStr = SecretStr("")


settings = Settings()
