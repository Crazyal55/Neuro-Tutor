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
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://localhost:5174", 
        "http://localhost:5177",
        "http://localhost:5180",  # Current frontend port
        "http://localhost:3000",  # Common development port
    ]
    
    # API settings
    api_prefix: str = "/api"
    
    # LLM Provider settings
    llm_provider: str = "openrouter"  # openrouter is the primary provider
    
    # Default model settings
    default_model: str = "qwen2.5:72b-instruct"
    default_temperature: float = 0.7
    default_max_tokens: int = 1000
    
    # Request settings
    request_timeout: int = 30  # seconds


# Global settings instance
settings = Settings()


def get_cors_config():
    """Get CORS configuration for FastAPI."""
    return {
        "allow_origins": settings.cors_origins,
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
