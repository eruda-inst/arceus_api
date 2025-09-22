from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    OPA_TOKEN: str
    IXC_TOKEN: str
    OPA_HOST: str
    IXC_HOST: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


settings = Settings()
