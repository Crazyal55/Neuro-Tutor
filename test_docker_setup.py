#!/usr/bin/env python3
"""
Docker Setup Verification Script for Neuro-Tutor
Tests all Docker services and functionality without relying on Docker CLI
"""

import requests
import json
import time
import sys
from datetime import datetime

def test_backend_health():
    """Test backend health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Backend Health: {health_data.get('status', 'Unknown')}")
            print(f"   Service: {health_data.get('service', 'Unknown')}")
            print(f"   Version: {health_data.get('version', 'Unknown')}")
            return True
        else:
            print(f"❌ Backend Health: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend Health: Connection failed - {e}")
        return False

def test_frontend_access():
    """Test frontend accessibility"""
    try:
        response = requests.get("http://localhost:5173", timeout=10)
        if response.status_code == 200:
            print(f"✅ Frontend Access: HTTP {response.status_code}")
            content_length = len(response.text)
            print(f"   Content Length: {content_length} characters")
            
            # Check for React app indicators
            if 'react' in response.text.lower() or 'vite' in response.text.lower():
                print("   ✅ React/Vite app detected")
            return True
        else:
            print(f"❌ Frontend Access: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend Access: Connection failed - {e}")
        return False

def test_api_functionality():
    """Test basic API functionality"""
    try:
        # Test API documentation
        response = requests.get("http://localhost:8000/docs", timeout=10)
        if response.status_code == 200:
            print("✅ API Documentation: Accessible")
        else:
            print(f"❌ API Documentation: HTTP {response.status_code}")
            return False
        
        # Test root endpoint
        response = requests.get("http://localhost:8000/", timeout=10)
        if response.status_code == 200:
            print("✅ Root Endpoint: Accessible")
        else:
            print(f"❌ Root Endpoint: HTTP {response.status_code}")
            return False
            
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ API Functionality: Connection failed - {e}")
        return False

def test_chat_api():
    """Test chat API with a simple message"""
    try:
        test_payload = {
            "messages": [
                {
                    "id": "test-msg",
                    "role": "user", 
                    "content": "Hello, this is a test message"
                }
            ],
            "preferences": {
                "verbosity_level": 2,
                "explanation_style": "step_by_step",
                "visual_aids": False,
                "reading_mode": "comfortable"
            }
        }
        
        response = requests.post(
            "http://localhost:8000/api/chat/",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Chat API: Test message sent successfully")
            data = response.json()
            
            # Check response structure
            if "reply_message" in data and "content" in data["reply_message"]:
                reply_content = data["reply_message"]["content"]
                print(f"   Response Length: {len(reply_content)} characters")
                print(f"   Response Preview: {reply_content[:100]}...")
                
                # Check if it's a real AI response or fallback
                if any(keyword in reply_content.lower() for keyword in ["trouble connecting", "technical difficulties", "configure your"]):
                    print("   ⚠️  Warning: Fallback response detected")
                    return False
                else:
                    print("   ✅ Real AI response detected")
                    return True
            else:
                print("   ❌ Invalid response structure")
                return False
        else:
            print(f"❌ Chat API: HTTP {response.status_code}")
            if response.text:
                print(f"   Error Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Chat API: Connection failed - {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Chat API: Invalid JSON response - {e}")
        return False

def main():
    """Run all Docker verification tests"""
    print("🐳 Docker Setup Verification for Neuro-Tutor")
    print("=" * 50)
    print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Frontend Access", test_frontend_access),
        ("API Functionality", test_api_functionality),
        ("Chat API", test_chat_api),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"🧪 Running: {test_name}")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
        print()
    
    # Summary
    print("📊 Test Results Summary")
    print("=" * 50)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 Docker setup is working perfectly!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
