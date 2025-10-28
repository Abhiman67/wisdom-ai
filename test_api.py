"""
Simple API test script for God AI Backend
Tests basic functionality of the API endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_signup():
    """Test user signup"""
    print("\nTesting user signup...")
    signup_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/signup", json=signup_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Token received: {data['access_token'][:20]}...")
        return data['access_token']
    else:
        print(f"Error: {response.text}")
        return None

def test_login():
    """Test user login"""
    print("\nTesting user login...")
    login_data = {
        "username": "test@example.com",  # FastAPI OAuth2PasswordRequestForm uses 'username'
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/login", data=login_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Token received: {data['access_token'][:20]}...")
        return data['access_token']
    else:
        print(f"Error: {response.text}")
        return None

def test_chat(token):
    """Test chat endpoint"""
    print("\nTesting chat endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    chat_data = {"message": "I'm feeling sad and need some comfort"}
    
    response = requests.post(f"{BASE_URL}/chat", json=chat_data, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Detected mood: {data['detected_mood']}")
        print(f"Verse ID: {data['verse_id']}")
        print(f"Reply: {data['reply'][:100]}...")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_daily_verse(token):
    """Test daily verse endpoint"""
    print("\nTesting daily verse endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/daily-verse", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Verse ID: {data['verse_id']}")
        print(f"Source: {data['source']}")
        print(f"Text: {data['text'][:100]}...")
        print(f"Audio URL: {data.get('audio_url', 'Not generated')}")
        print(f"Image URL: {data.get('image_url', 'Not generated')}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_profile(token):
    """Test profile endpoint"""
    print("\nTesting profile endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/profile", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"User: {data['name']} ({data['email']})")
        print(f"Last mood: {data['last_mood']}")
        print(f"Chat history entries: {len(data['chat_history'])}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_save_verse(token):
    """Test save verse endpoint"""
    print("\nTesting save verse endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    save_data = {"verse_id": "Gita_2.47"}
    
    response = requests.post(f"{BASE_URL}/save-verse", json=save_data, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Save result: {data['message']}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_my_saved_verses(token):
    """Test my saved verses endpoint"""
    print("\nTesting my saved verses endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/my-saved-verses", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Saved verses count: {len(data['saved_verses'])}")
        for verse in data['saved_verses']:
            print(f"  - {verse['verse_id']}: {verse['text'][:50]}...")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def main():
    """Run all API tests"""
    print("🧪 Testing God AI Backend API")
    print("=" * 50)
    
    # Test health endpoint
    if not test_health():
        print("❌ Health check failed. Is the server running?")
        return
    
    # Test signup
    token = test_signup()
    if not token:
        print("❌ Signup failed")
        return
    
    # Wait a moment for database operations
    time.sleep(1)
    
    # Test other endpoints
    tests = [
        test_login,
        lambda: test_chat(token),
        lambda: test_daily_verse(token),
        lambda: test_profile(token),
        lambda: test_save_verse(token),
        lambda: test_my_saved_verses(token)
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        time.sleep(0.5)  # Small delay between tests
    
    print(f"\n✅ Tests completed: {passed}/{len(tests) + 1} passed")
    
    if passed == len(tests) + 1:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()
