#!/usr/bin/env python3
"""
Simple test script to verify OpenRouter API key configuration
"""

import os
import sys
sys.path.append('backend')

from app.core.config import settings
from app.core.openrouter_secrets import get_openrouter_api_key, get_default_model

print("=== OpenRouter API Key Test ===")
print(f"Settings API Key Length: {len(settings.openrouter_api_key) if settings.openrouter_api_key else 0}")
print(f"Settings API Key First 10: {settings.openrouter_api_key[:10] if settings.openrouter_api_key else 'None'}")
print(f"Get API Key Length: {len(get_openrouter_api_key())}")
print(f"Get API Key First 10: {get_openrouter_api_key()[:10]}")
print(f"Default Model: {get_default_model()}")
print(f"Settings Default Model: {settings.default_model}")

# Check if API key looks valid
api_key = get_openrouter_api_key()
if api_key and api_key != "YOUR_OPENROUTER_API_KEY_HERE":
    print("✅ API Key appears to be configured correctly")
else:
    print("❌ API Key is not configured properly")

# Test environment variable directly
env_key = os.getenv("OPENROUTER_API_KEY")
print(f"Direct ENV API Key Length: {len(env_key) if env_key else 0}")
print(f"Direct ENV API Key First 10: {env_key[:10] if env_key else 'None'}")
