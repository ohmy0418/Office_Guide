from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql+psycopg2://office:office@localhost:5432/office_guide"
    API_V1_PREFIX: str = "/api/v1"
    EMBEDDING_DIMENSION: int = 1536
    STORAGE_ROOT: str = "./var/storage"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
