"""
Configuration module for the Email Assistant application.
Handles environment variables and application settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Google OAuth
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str

    # AI Provider Configuration
    ai_provider: str = "openai"  # DEFAULT: openai (was gemini)
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

    # Application
    secret_key: str
    frontend_url: str
    backend_url: str
    session_expire_hours: int = 24
    environment: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
