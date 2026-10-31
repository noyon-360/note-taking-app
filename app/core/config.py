from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # App
    APP_NAME: str = "Secure Note-Taking Application"
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "127.0.0.1"
    PORT: int

    # Database
    DATABASE_URL: str
    DATABASE_NAME: str


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
