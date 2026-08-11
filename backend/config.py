"""Application configuration."""

from functools import lru_cache

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database — set DATABASE_URL for PostgreSQL (deploy); leave empty for local DuckDB
    database_url: str = ""

    # LLM provider: groq | gemini | openai
    llm_provider: str = "groq"

    # Groq (recommended — free tier, fast)
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # Google Gemini
    google_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # OpenAI (optional)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    max_sql_retries: int = 3
    max_query_rows: int = 200

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def agents_ready(self) -> bool:
        provider = self.llm_provider.lower()
        if provider == "groq":
            return bool(self.groq_api_key)
        if provider == "gemini":
            return bool(self.google_api_key)
        if provider == "openai":
            return bool(self.openai_api_key)
        return False

    def active_model(self) -> str:
        provider = self.llm_provider.lower()
        if provider == "groq":
            return self.groq_model
        if provider == "gemini":
            return self.gemini_model
        return self.openai_model

    def db_backend(self) -> str:
        return "postgres" if self.database_url else "duckdb"


@lru_cache
def get_settings() -> Settings:
    return Settings()
