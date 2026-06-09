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
    
    # Database settings
    database_url: str = "sqlite:///./neuro_tutor.db"

    # Default model settings (canonical default — override via DEFAULT_MODEL env)
    default_model: str = "openai/gpt-3.5-turbo"
    default_temperature: float = 0.7
    default_max_tokens: int = 1000
    
    # Request settings
    request_timeout: int = 30  # seconds
    rate_limit_per_minute: int = 20
    auto_migrate: bool = True

    # Vector store / RAG settings
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "materials"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_dimension: int = 384
    rag_top_k: int = 5
    rag_score_threshold: float = 0.35
    upload_max_bytes: int = 50 * 1024 * 1024
    uploads_dir: str = "./data/uploads"


# Global settings instance
settings = Settings()


def get_cors_config():
    """Get CORS configuration for FastAPI."""
    return {
        "allow_origins": settings.cors_origins_list,
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
    }
