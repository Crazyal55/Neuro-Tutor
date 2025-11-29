"""
Test script for OpenRouter integration.
Run this script to test OpenRouter API connection.
"""

import asyncio
from app.core.openrouter_secrets import get_openrouter_api_key
import httpx

async def test_openrouter():
    """Test OpenRouter API connection."""
    
    api_key = get_openrouter_api_key()
    model = "qwen2.5:72b-instruct"
    
    if not api_key or api_key == "YOUR_OPENROUTER_API_KEY_HERE":
        print("❌ Please set OPENROUTER_API_KEY in your .env file")
        return
    
    print(f"🧠 Testing OpenRouter API with model: {model}")
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://neurotutor.local",
            "X-Title": "NeuroTutor-Dev"
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a helpful Socratic tutor who guides students through questions."
                },
                {
                    "role": "user", 
                    "content": "Can you help me understand photosynthesis? I don't know where to start."
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                reply = data["choices"][0]["message"]["content"]
                print("✅ OpenRouter API connection successful!")
                print("\n📝 Sample response:")
                print("-" * 50)
                print(reply)
                print("-" * 50)
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_openrouter())
