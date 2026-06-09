"""
Manual OpenRouter connectivity test.

Run from the backend directory:
    python -m scripts.test_openrouter
"""

import asyncio
import httpx

from app.core.openrouter_secrets import get_openrouter_api_key, get_default_model


async def test_openrouter() -> None:
    api_key = get_openrouter_api_key()
    model = get_default_model()

    if not api_key or api_key == "YOUR_OPENROUTER_API_KEY_HERE":
        print("Please set OPENROUTER_API_KEY in backend/.env")
        return

    print(f"Testing OpenRouter API with model: {model}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://neurotutor.local",
        "X-Title": "NeuroTutor-Dev",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful Socratic tutor who guides students through questions.",
            },
            {
                "role": "user",
                "content": "Can you help me understand photosynthesis? I don't know where to start.",
            },
        ],
        "temperature": 0.7,
        "max_tokens": 500,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
            )

            if response.status_code == 200:
                data = response.json()
                reply = data["choices"][0]["message"]["content"]
                print("OpenRouter API connection successful.")
                print("\nSample response:")
                print("-" * 50)
                print(reply)
                print("-" * 50)
            else:
                print(f"API error: {response.status_code}")
                print(f"Response: {response.text}")
    except Exception as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    asyncio.run(test_openrouter())
