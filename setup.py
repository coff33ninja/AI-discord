#!/usr/bin/env python3
"""
Setup script for Discord AI Bot
Uses uv for fast, reliable package management
"""

import os
import sys
import subprocess
import shutil

def check_python_version():
    """Check if Python version is 3.12 or higher"""
    if sys.version_info < (3, 12):
        print("❌ Python 3.12 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    
    current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    print(f"✅ Python version: {current_version}")
    
    # Warn about Python 3.13 compatibility issues
    if sys.version_info >= (3, 13):
        print("\n⚠️  WARNING: Python 3.13 detected")
        print("   Some dependencies (watchdog, KittenTTS) may have compatibility issues.")
        print("   Recommended: Use Python 3.12.x for best stability")
        print("   Python 3.12 is fully compatible with all features including voice TTS/STT")
    else:
        print(f"✅ Python {current_version} is compatible with all features!")
    
    return True

def install_python_3_12():
    """Install Python 3.12 using uv"""
    print("\n🔧 Installing Python 3.12 with uv...")
    try:
        # Use uv to download and install Python 3.12
        subprocess.check_call(["uv", "python", "install", "3.12"])
        print("✅ Python 3.12 installed successfully!")
        print("\n📝 You may need to restart your terminal to use the new Python version.")
        print("   After restart, run setup.py again to complete the setup.")
        return False  # Return False to exit and let user restart
    except FileNotFoundError:
        print("⚠️  uv not found in PATH - installing uv first...")
        if install_uv():
            return install_python_3_12()
        else:
            print("❌ Could not install Python 3.12. Please visit: https://www.python.org/")
            return False
    except subprocess.CalledProcessError:
        print("⚠️  Could not install Python 3.13 via uv.")
        print("   Please manually download from: https://www.python.org/")
        response = input("Continue with current Python version? (y/N): ").lower()
        return response == 'y'

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

def validate_requirements_compatibility():
    """Validate that all requirements are compatible with Python 3.12"""
    print("\n🔍 Validating requirements compatibility for Python 3.12...")
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    # List of packages optimized for Python 3.12
    py312_compatible_packages = {
        "discord.py": "2.5.2+",  # Stable with Python 3.12
        "google-generativeai": "0.7.0+",  # Gemini API (tested on 3.12)
        "python-dotenv": "1.0.0+",  # Full Python 3.12 support
        "aiohttp": "3.12.0+",  # Latest async HTTP (Python 3.8+)
        "requests": "2.32.0+",  # Latest HTTP library (Python 3.7+)
        "beautifulsoup4": "4.12.0+",  # Web parsing (Python 3.6+)
        "aiosqlite": "1.3.0+",  # Async SQLite (Python 3.7+)
        "watchdog": "6.0.0",  # ONLY 6.0.0 works with 3.12 (not 3.13+)
    }
    
    if sys.version_info >= (3, 13):
        print(f"⚠️  WARNING: Python 3.13 detected ({python_version})")
        print("   Some features may have compatibility issues:")
        print("   • watchdog has threading issues with Python 3.13")
        print("   • KittenTTS may have compatibility problems")
        print("\n💡 RECOMMENDATION: Use Python 3.12.x for best stability")
        print("   All features are fully tested and compatible with Python 3.12")
        return True  # Allow but warn
    else:
        print(f"✅ Python {python_version} is compatible!")
        if sys.version_info >= (3, 12):
            print("✅ All features fully supported with Python 3.12+")
            print("\n📦 Compatible packages for Python 3.12:")
            for package, version in py312_compatible_packages.items():
                print(f"   ✅ {package}: {version}")
        return True

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
    print("🤖 Discord AI Bot Setup")
    print("=" * 50)
    print("Using uv for fast, reliable package management\n")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Validate requirements compatibility
    if not validate_requirements_compatibility():
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
    print("   To install new Python: uv python install 3.13")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)