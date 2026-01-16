"""
Application Configuration

Centralized configuration management using environment variables.
"""
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        app_name: Name of the application.
        debug: Enable debug mode.
        secret_key: Secret key for JWT tokens.
        mongodb_url: MongoDB connection URL.
        database_name: Name of the MongoDB database.
        access_token_expire_minutes: JWT token expiration time.
        cors_origins: Allowed CORS origins.
    """

    # Application
    app_name: str = "Task Manager API"
    debug: bool = False
    environment: str = "development"

    # Security
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60

    # Database
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "taskmanager"

    # CORS
    cors_origins: str = "*"

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds

    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> list:
        """Get CORS origins as a list."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.

    Uses LRU cache to avoid re-reading environment variables.
    """
    return Settings()
