#!/usr/bin/env python3
"""
Setup script for Coffee - Tsundere AI Discord Bot
"""

import os
import sys
import subprocess
import shutil

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements!")
        return False

def setup_env_file():
    """Set up environment file"""
    print("\n🔧 Setting up environment file...")
    
    if os.path.exists(".env"):
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("Skipping .env setup...")
            return True
    
    if os.path.exists(".env.example"):
        shutil.copy(".env.example", ".env")
        print("✅ Created .env file from template")
        print("\n📝 Please edit .env file and add your API keys:")
        print("   - DISCORD_TOKEN (required)")
        print("   - GEMINI_API_KEY (required)")
        print("   - OPENWEATHER_API_KEY (optional)")
        return True
    else:
        print("❌ .env.example not found!")
        return False

def main():
    """Main setup function"""
    print("🤖 Coffee - Tsundere AI Discord Bot Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Setup environment file
    if not setup_env_file():
        return False
    
    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run: python bot.py")
    print("\n💡 Need help getting API keys? Check the README.md!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)