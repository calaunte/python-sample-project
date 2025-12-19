"""Application configuration management."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    # Application metadata
    app_name: str = "IP Geolocation Service"
    app_version: str = "1.0.0"
    debug: bool = False

    # API configuration
    api_v1_prefix: str = "/api/v1"

    # Provider configuration
    provider_name: str = "ip-api.com"
    provider_base_url: str = "http://ip-api.com/json"
    provider_timeout: int = 5  # seconds

    # CORS configuration
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["GET"]
    cors_allow_headers: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
settings = Settings()
