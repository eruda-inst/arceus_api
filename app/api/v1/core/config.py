from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    OPA_TOKEN: str
    IXC_TOKEN: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )

settings = Settings()