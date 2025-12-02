"""
Core configuration settings for Neuro Tutor backend.
"""

from typing import List
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Allow extra fields from environment
    )
    
    # App settings
    app_name: str = "Neuro Tutor API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # CORS settings for Vite development
    cors_origins: str = "http://localhost:5173,http://localhost:5174,http://localhost:5177,http://localhost:5180,http://localhost:3000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated CORS origins string to list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
    
    # API settings
    api_prefix: str = "/api"
    
    # LLM Provider settings
    llm_provider: str = "openrouter"  # openrouter is the primary provider
    openrouter_api_key: str = "YOUR_OPENROUTER_API_KEY_HERE"  # OpenRouter API key
    
    @property
    def openrouter_api_key_from_env(self) -> str:
        """Get OpenRouter API key from environment variable."""
        import os
        env_key = os.getenv("OPENROUTER_API_KEY")
        return env_key if env_key else self.openrouter_api_key
    
    # Default model settings
    default_model: str = "openai/gpt-3.5-turbo"  # Use widely supported model
    default_temperature: float = 0.7
    default_max_tokens: int = 1000
    
    # Request settings
    request_timeout: int = 30  # seconds


# Global settings instance
settings = Settings()


def get_cors_config():
    """Get CORS configuration for FastAPI."""
    return {
        "allow_origins": settings.cors_origins_list,
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
