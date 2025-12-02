"""
OpenRouter API key management.

This file is for development convenience only.
In production, ALWAYS use environment variables / secret manager.
"""

import os
from functools import lru_cache

# WARNING:
# This file is for development convenience only.
# In production, ALWAYS use environment variables / secret manager.

DEFAULT_OPENROUTER_API_KEY = "YOUR_OPENROUTER_API_KEY_HERE"


@lru_cache
def get_openrouter_api_key() -> str:
    """
    Get OpenRouter API key from settings with environment fallback.
    
    Returns:
        str: OpenRouter API key
    """
    from app.core.config import settings
    return settings.openrouter_api_key_from_env


@lru_cache
def get_default_model() -> str:
    """
    Get default model from environment or fallback.
    
    Returns:
        str: Default model name
    """
    return os.getenv("DEFAULT_MODEL", "openai/gpt-3.5-turbo")
