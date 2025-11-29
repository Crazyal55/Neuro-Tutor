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
    Get OpenRouter API key from environment or default.
    
    Returns:
        str: OpenRouter API key
    """
    return os.getenv("OPENROUTER_API_KEY", DEFAULT_OPENROUTER_API_KEY)


@lru_cache
def get_default_model() -> str:
    """
    Get default model from environment or fallback.
    
    Returns:
        str: Default model name
    """
    return os.getenv("DEFAULT_MODEL", "qwen2.5:7b-instruct")
