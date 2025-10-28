"""
Simple startup script for God AI Backend
Handles database initialization and server startup
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required files exist"""
    required_files = ["main.py", "requirements.txt", "database_init.py"]
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✓ All required files found")
    return True

def setup_environment():
    """Set up environment files and directories"""
    # Create .env if it doesn't exist
    if not Path(".env").exists() and Path("env.example").exists():
        print("Creating .env file from template...")
        with open("env.example", "r") as src:
            content = src.read()
        with open(".env", "w") as dst:
            dst.write(content)
        print("✓ .env file created")
    
    # Create media directories
    media_dirs = ["media", "media/audio", "media/images"]
    for dir_path in media_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("✓ Media directories created")

def install_dependencies():
    """Install Python dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✓ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def initialize_database():
    """Initialize database with admin user and seed data"""
    print("Initializing database...")
    try:
        subprocess.run([sys.executable, "database_init.py"], check=True, capture_output=True)
        print("✓ Database initialized")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to initialize database: {e}")
        return False

def start_server():
    """Start the development server"""
    print("\n🚀 Starting God AI Backend Server...")
    print("=" * 50)
    print("Server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Admin Login: admin@godai.com / admin123")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--reload", 
            "--port", "8000",
            "--host", "0.0.0.0"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")

def main():
    """Main startup function"""
    print("🙏 God AI Backend - Spiritual Companion")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies. Please check your Python environment.")
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        print("❌ Failed to initialize database.")
        sys.exit(1)
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
