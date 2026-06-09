#!/usr/bin/env python3
"""Verify OpenRouter API key and default model configuration."""

from app.core.config import settings
from app.core.openrouter_secrets import get_openrouter_api_key, get_default_model


def main() -> None:
    print("=== OpenRouter configuration ===")
    print(f"Default model: {get_default_model()}")
    print(f"Settings default model: {settings.default_model}")
    print(f"Database URL: {settings.database_url}")

    api_key = get_openrouter_api_key()
    if api_key and api_key not in ("YOUR_OPENROUTER_API_KEY_HERE", "your-openrouter-api-key-here"):
        print("API key: configured")
    else:
        print("API key: not configured")


if __name__ == "__main__":
    main()
