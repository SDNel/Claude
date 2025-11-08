"""Application configuration."""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    cors_allow_credentials: bool = True

    # Security
    default_timeout_ms: int = 1000
    max_timeout_ms: int = 5000
    max_expression_length: int = 10000

    # Performance
    max_workers: int = 4
    backend_name: str = "remote-sympy"

    # Logging
    log_format: str = "json"
    redact_expressions: bool = True

    # AI Configuration
    anthropic_api_key: str = ""  # Loaded from .env


settings = Settings()
