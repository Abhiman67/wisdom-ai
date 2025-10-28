#!/usr/bin/env python3
"""
Grok API Setup Script for God AI
Helps configure Grok API integration
"""

import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

def setup_grok():
    """Setup Grok API configuration"""
    print("🚀 Setting up Grok API integration for God AI...")
    print("=" * 50)
    
    # Get Grok API key
    api_key = input("Enter your Grok API key (get it from https://x.ai/): ").strip()
    
    if not api_key:
        print("❌ No API key provided. Skipping Grok setup.")
        return False
    
    # Update .env file
    env_file = Path(".env")
    
    if not env_file.exists():
        # Create .env file
        env_content = """# God AI Configuration
JWT_SECRET=change_this_secret_key_please
DATABASE_URL=sqlite:///./god_ai.db
MEDIA_ROOT=./media

# LLM Configuration
USE_GROK=true
GROK_API_KEY={}
GROK_API_URL=https://api.x.ai/v1/chat/completions
USE_OLLAMA=false
OLLAMA_URL=http://localhost:11434
""".format(api_key)
        
        env_file.write_text(env_content)
        print("✓ Created .env file with Grok configuration")
    else:
        # Update existing .env file
        env_content = env_file.read_text()
        
        # Remove existing Grok settings
        lines = env_content.split('\n')
        filtered_lines = []
        for line in lines:
            if not line.startswith('USE_GROK=') and not line.startswith('GROK_API_KEY=') and not line.startswith('GROK_API_URL='):
                filtered_lines.append(line)
        
        # Add new Grok settings
        filtered_lines.extend([
            "",
            "# LLM Configuration",
            "USE_GROK=true",
            f"GROK_API_KEY={api_key}",
            "GROK_API_URL=https://api.x.ai/v1/chat/completions",
            "USE_OLLAMA=false",
            "OLLAMA_URL=http://localhost:11434"
        ])
        
        env_file.write_text('\n'.join(filtered_lines))
        print("✓ Updated .env file with Grok configuration")
    
    print("\n🎉 Grok API setup complete!")
    print("Your God AI backend will now use Grok for generating responses.")
    print("\nTo start the server, run: python main.py")
    print("\nNote: Grok API usage may incur costs. Check https://x.ai/pricing for details.")
    
    return True

def test_grok_connection():
    """Test Grok API connection"""
    print("\n🧪 Testing Grok API connection...")
    
    try:
        from llm_service import LLMService
        import os
        import requests
        # Print env variables for debugging
        print(f"USE_GROK: {os.getenv('USE_GROK')}")
        print(f"GROK_API_KEY: {os.getenv('GROK_API_KEY')[:8]}... (hidden)")
        print(f"GROK_API_URL: {os.getenv('GROK_API_URL')}")

        # Directly test Grok API connection
        api_key = os.getenv('GROK_API_KEY')
        api_url = os.getenv('GROK_API_URL')
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "grok-beta",
            "messages": [
                {"role": "system", "content": "Test connection."},
                {"role": "user", "content": "Hello, Grok!"}
            ],
            "max_tokens": 10
        }
        try:
            r = requests.post(api_url, json=payload, headers=headers, timeout=15)
            print(f"Grok API status: {r.status_code}")
            print(f"Grok API response: {r.text}")
        except Exception as api_e:
            print(f"Exception during direct Grok API call: {api_e}")

        # Also test via LLMService
        llm = LLMService()
        if llm.use_grok:
            print("✓ Grok API connection successful (via LLMService)")
            test_verse = {
                "text": "The Lord is my shepherd; I shall not want.",
                "source": "Bible - Psalms"
            }
            response = llm.generate_response(
                user_message="I am feeling sad and need comfort",
                verse=test_verse,
                mood="sadness"
            )
            print(f"✓ Test response generated: {response[:100]}...")
            return True
        else:
            print("❌ Grok API not configured properly (via LLMService)")
            return False
    except Exception as e:
        print(f"❌ Grok test failed: {e}")
        return False

def main():
    """Main setup function"""
    if setup_grok():
        test_grok_connection()

if __name__ == "__main__":
    main()
