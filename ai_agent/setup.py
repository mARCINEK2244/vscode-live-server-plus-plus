#!/usr/bin/env python3
"""
Setup script for AI Agent system.
"""

import os
import sys
import subprocess
from pathlib import Path

def install_requirements():
    """Install Python requirements."""
    print("Installing Python dependencies...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

def setup_environment():
    """Set up the environment."""
    print("Setting up AI Agent environment...")
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        print("Creating .env file from template...")
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("Please edit .env file with your API keys and configuration.")
        else:
            print("Warning: .env.example not found!")

def create_directories():
    """Create necessary directories."""
    directories = [
        'templates',
        'logs',
        'data'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"Created directory: {directory}")

def main():
    """Main setup function."""
    print("🤖 AI Agent Setup")
    print("=" * 50)
    
    try:
        create_directories()
        install_requirements()
        setup_environment()
        
        print("\n✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit the .env file with your API keys")
        print("2. Run the web interface: python app.py")
        print("3. Or run the CLI: python cli_agent.py")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()