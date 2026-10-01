from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LegalEase"
    app_version: str = "1.0.0"
    environment: str = "development"

    gemini_api_key: str = ""
    # Current default. Set GEMINI_MODEL=gemini-1.5-pro if your account still supports it.
    gemini_model: str = "gemini-2.5-flash"
    gemini_temperature: float = 0.25
    gemini_max_output_tokens: int = 8192

    backend_url: str = "http://127.0.0.1:8000"
    request_timeout_seconds: int = 120
    max_input_chars: int = 20000

    cors_origins: str = "http://localhost:8501,http://127.0.0.1:8501"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
