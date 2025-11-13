#!/usr/bin/env python3
"""
Setup script for Akino - Tsundere AI Discord Bot
Uses uv for fast, reliable package management
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

def install_uv():
    """Install uv package manager"""
    print("\n📦 Installing uv package manager...")
    try:
        # First try to install uv via pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", "uv"])
        print("✅ uv installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Failed to install uv via pip, attempting alternative installation...")
        try:
            # Try using pip's --user flag
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "uv"])
            print("✅ uv installed successfully (user mode)!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install uv!")
            print("   Please install uv manually: https://github.com/astral-sh/uv")
            return False

def check_uv_installed():
    """Check if uv is installed and accessible"""
    try:
        subprocess.check_call(["uv", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def create_venv_with_uv():
    """Create virtual environment using uv"""
    print("\n🔧 Creating virtual environment with uv...")
    try:
        # Determine venv name based on OS
        venv_name = ".venv"
        subprocess.check_call(["uv", "venv", venv_name])
        print(f"✅ Virtual environment created: {venv_name}")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment with uv!")
        return False

def install_requirements_with_uv():
    """Install required packages using uv"""
    print("\n📦 Installing requirements with uv...")
    try:
        subprocess.check_call(["uv", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully with uv!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements with uv!")
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
        print("   - DISCORD_BOT_TOKEN (required)")
        print("   - GEMINI_API_KEY (required)")
        print("   - OPENWEATHER_API_KEY (optional)")
        return True
    else:
        print("❌ .env.example not found!")
        return False

def main():
    """Main setup function"""
    print("🤖 Akino - Tsundere AI Discord Bot Setup")
    print("=" * 50)
    print("Using uv for fast, reliable package management\n")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install uv
    if not install_uv():
        return False
    
    # Verify uv is accessible
    if not check_uv_installed():
        print("❌ uv is installed but not accessible in PATH!")
        print("   Please ensure uv is added to your system PATH or restart your terminal.")
        return False
    
    print("✅ uv is ready!")
    
    # Create virtual environment with uv
    if not create_venv_with_uv():
        return False
    
    # Install requirements with uv
    if not install_requirements_with_uv():
        return False
    
    # Setup environment file
    if not setup_env_file():
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Setup complete!")
    print("=" * 50)
    
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Activate venv: .venv\\Scripts\\activate (Windows) or source .venv/bin/activate (Linux/Mac)")
    print("3. Run: python bot.py")
    print("\n💡 Using uv for faster installs and synced dependencies!")
    print("   To update packages: uv pip install --upgrade <package>")
    print("   To sync all: uv pip install -r requirements.txt")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)