#!/usr/bin/env python3
"""
Setup script for God AI LLM integration
Helps install and configure open-source LLM models
"""

import os
import subprocess
import sys
import requests
import json
from pathlib import Path

def check_ollama_installation():
    """Check if Ollama is installed and running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✓ Ollama is installed and running")
            return True
    except:
        pass
    
    print("❌ Ollama is not installed or not running")
    return False

def install_ollama():
    """Install Ollama"""
    print("Installing Ollama...")
    
    if sys.platform == "win32":
        print("Please download and install Ollama from: https://ollama.ai/download")
        print("After installation, run: ollama serve")
        return False
    elif sys.platform == "darwin":
        # macOS
        subprocess.run(["brew", "install", "ollama"], check=True)
    else:
        # Linux
        subprocess.run(["curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"], shell=True, check=True)
    
    print("✓ Ollama installed successfully")
    return True

def download_llm_model():
    """Download a lightweight LLM model"""
    print("Downloading Llama 2 7B model (this may take a while)...")
    
    try:
        # Download Llama 2 7B model
        result = subprocess.run(["ollama", "pull", "llama2:7b"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Llama 2 7B model downloaded successfully")
            return True
        else:
            print(f"❌ Failed to download model: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        return False

def test_llm_generation():
    """Test LLM generation"""
    print("Testing LLM generation...")
    
    try:
        payload = {
            "model": "llama2:7b",
            "prompt": "Hello, how are you?",
            "stream": False
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ LLM test successful: {result.get('response', '')[:100]}...")
            return True
        else:
            print(f"❌ LLM test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ LLM test error: {e}")
        return False

def setup_environment():
    """Setup environment variables"""
    env_file = Path(".env")
    
    if not env_file.exists():
        # Create .env file from example
        example_file = Path("env.example")
        if example_file.exists():
            env_file.write_text(example_file.read_text())
            print("✓ Created .env file from example")
    
    # Add LLM configuration to .env
    env_content = env_file.read_text() if env_file.exists() else ""
    
    if "USE_OLLAMA=true" not in env_content:
        env_content += "\n# LLM Configuration\nUSE_OLLAMA=true\nOLLAMA_URL=http://localhost:11434\n"
        env_file.write_text(env_content)
        print("✓ Added LLM configuration to .env file")

def main():
    """Main setup function"""
    print("🚀 Setting up God AI LLM integration...")
    print("=" * 50)
    
    # Check if Ollama is installed
    if not check_ollama_installation():
        print("\n📥 Installing Ollama...")
        if not install_ollama():
            print("Please install Ollama manually and run this script again.")
            return
    
    # Download model
    print("\n📦 Downloading LLM model...")
    if not download_llm_model():
        print("Failed to download model. You can try manually with: ollama pull llama2:7b")
        return
    
    # Test generation
    print("\n🧪 Testing LLM generation...")
    if not test_llm_generation():
        print("LLM test failed. Please check Ollama installation.")
        return
    
    # Setup environment
    print("\n⚙️ Setting up environment...")
    setup_environment()
    
    print("\n🎉 Setup complete!")
    print("Your God AI backend now supports open-source LLM generation.")
    print("\nTo start the server, run: python main.py")

if __name__ == "__main__":
    main()
