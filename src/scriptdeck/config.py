from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App configuration, read from environment variables and the .env file."""

    model_config = SettingsConfigDict(env_file=".env")

    database_url: str


settings = Settings()
