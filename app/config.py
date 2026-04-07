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

    OPENAI_API_KEY: str = ""
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # 텍스트가 이보다 적으면 OCR 경로 검토 (문자 수 기준)
    OCR_TEXT_THRESHOLD_CHARS: int = 80
    # chunk 목표 토큰(대략) — specify 300~800 권장, 상한 여유
    CHUNK_TARGET_TOKENS: int = 700
    CHUNK_MAX_TOKENS: int = 1200
    # OCRmyPDF 언어 (Tesseract)
    OCR_LANG: str = "kor+eng"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
