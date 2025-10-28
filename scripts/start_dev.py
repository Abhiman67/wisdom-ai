"""
Development startup script for God AI Backend
Handles environment setup, database initialization, and server startup
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def setup_environment():
    """Set up development environment"""
    print("Setting up development environment...")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists() and env_example.exists():
        print("Creating .env file from template...")
        subprocess.run(["cp", "env.example", ".env"], check=True)
        print("✓ .env file created. Please edit it with your configuration.")
    
    # Create media directories
    media_dirs = ["media", "media/audio", "media/images"]
    for dir_path in media_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✓ Media directories created")

def install_dependencies():
    """Install Python dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✓ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def initialize_database():
    """Initialize database with admin user and seed data"""
    print("Initializing database...")
    try:
        subprocess.run([sys.executable, "database_init.py"], check=True)
        print("✓ Database initialized")
    except subprocess.CalledProcessError as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)

def start_server():
    """Start the development server"""
    print("Starting development server...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--reload", 
            "--port", "8000",
            "--host", "0.0.0.0"
        ], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    print("🚀 Starting God AI Backend Development Environment")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Setup environment
    setup_environment()
    
    # Install dependencies
    install_dependencies()
    
    # Initialize database
    initialize_database()
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
