"""Application configuration using Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # HuggingFace
    hf_token: str
    model_name: str
    hf_endpoint_url: str

    # API Authentication
    api_keys: str

    # Server
    host: str
    port: int
    log_level: str

    # Generation Parameters
    max_new_tokens: int
    temperature: float

    # Request timeout in seconds (default 5 minutes)
    request_timeout: float = 300.0

    # System prompt for the genetics assistant
    system_prompt: str

    # CORS origins (comma-separated)
    cors_origins: str = "*"

    @property
    def cors_origins_list(self) -> list[str]:
        """Return CORS origins as a list."""
        if not self.cors_origins or self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def api_keys_list(self) -> list[str]:
        """Return API keys as a list."""
        if not self.api_keys:
            return []
        return [key.strip() for key in self.api_keys.split(",") if key.strip()]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
