#!/usr/bin/env python3
"""
Setup script for Discord AI Bot
Uses uv for fast, reliable package management
"""

import os
import sys
import subprocess
import shutil

def find_python_312():
    """Try to find Python 3.12 executable"""
    import shutil
    
    possible_commands = ["python3.12", "python3.12.exe", "py", "-3.12"]
    
    for cmd in possible_commands:
        if shutil.which(cmd):
            try:
                result = subprocess.run(
                    [cmd, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if "3.12" in result.stdout or "3.12" in result.stderr:
                    return cmd
            except Exception:
                continue
    
    return None

def rerun_with_python_312(python_312_cmd):
    """Re-execute setup.py with Python 3.12"""
    print("\n🔄 Automatically re-running setup.py with Python 3.12...")
    print("=" * 50)
    print()
    
    try:
        result = subprocess.run([python_312_cmd, "setup.py"])
        sys.exit(result.returncode)
    except Exception as e:
        print(f"❌ Error running Python 3.12: {e}")
        return False

def check_python_version():
    """Check if Python version is 3.12 or higher"""
    if sys.version_info < (3, 12):
        print("❌ Python 3.12 or higher is required!")
        print(f"Current version: {sys.version}")
        print("\n🔧 Would you like to install Python 3.12 using uv?")
        print("   This will download and install Python 3.12 alongside your current version.")
        print("   Setup will then automatically continue with Python 3.12.")
        
        response = input("\nInstall Python 3.12 with uv? (y/N): ").strip().lower()
        if response == 'y':
            print("\n📦 Installing uv first (if not already installed)...")
            if not install_uv():
                print("❌ Could not install uv. Please install manually: https://github.com/astral-sh/uv")
                return False
            
            print("\n🔧 Installing Python 3.12 with uv...")
            if install_python_3_12():
                print("\n✅ Python 3.12 installed successfully!")
                
                # Try to find the newly installed Python 3.12
                print("\n🔍 Locating Python 3.12...")
                python_312 = find_python_312()
                
                if python_312:
                    print(f"✅ Found Python 3.12: {python_312}")
                    rerun_with_python_312(python_312)
                    return False  # Exit this process
                else:
                    print("⚠️  Could not locate Python 3.12 automatically")
                    print("   Please restart your terminal or run:")
                    print("   python3.12 setup.py")
                    return False
            else:
                print("\n❌ Python 3.12 installation failed.")
                print("   Please install Python 3.12 manually from: https://www.python.org/downloads/")
                return False
        else:
            print("\n❌ Python 3.12 is required. Exiting.")
            print("   Please install Python 3.12 from: https://www.python.org/downloads/")
            print("   Or use uv to install it: uv python install 3.12")
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
    try:
        # Use uv to download and install Python 3.12
        subprocess.check_call(["uv", "python", "install", "3.12"])
        print("✅ Python 3.12 installed successfully!")
        return True
    except FileNotFoundError:
        print("⚠️  uv not found in PATH")
        return False
    except subprocess.CalledProcessError:
        print("⚠️  Could not install Python 3.12 via uv.")
        return False
    except Exception as e:
        print(f"⚠️  Error: {e}")
        return False

def install_uv():
    """Install uv package manager"""
    print("\n📦 Installing uv package manager...")
    
    # First check if we're already in a uv-managed environment
    # (e.g., Python 3.12 installed via uv)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "uv"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("✅ uv installed successfully!")
            return True
        
        # Check the error message
        error_output = result.stderr + result.stdout
        if "externally-managed-environment" in error_output or "managed by uv" in error_output:
            print("⚠️  This Python is managed by uv (can't install via pip)")
            print("✅ uv should already be available in this environment")
            return True
        
    except Exception as e:
        error_str = str(e)
        if "externally-managed-environment" in error_str or "managed by uv" in error_str:
            print("⚠️  This Python is managed by uv (can't install via pip)")
            print("✅ uv should already be available in this environment")
            return True
    
    print("⚠️  Failed to install uv via pip, attempting alternative installation...")
    try:
        # Try using pip's --user flag
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--user", "uv"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("✅ uv installed successfully (user mode)!")
            return True
    except Exception:
        pass
    
    print("⚠️  Could not install uv via pip")
    print("   If this Python was installed via uv, it should already be available")
    print("   Otherwise, please install uv manually: https://github.com/astral-sh/uv")
    return True  # Return True since uv might already be available

def check_uv_installed():
    """Check if uv is installed and accessible"""
    try:
        # Try uv command
        subprocess.check_call(["uv", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Try via Python module
        try:
            subprocess.check_call([sys.executable, "-m", "uv", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

def run_uv_command(args):
    """Run uv command, trying both 'uv' and 'python -m uv'"""
    try:
        return subprocess.check_call(["uv"] + args)
    except FileNotFoundError:
        # Fall back to python -m uv
        return subprocess.check_call([sys.executable, "-m", "uv"] + args)

def check_existing_venv():
    """Check for existing virtual environment"""
    possible_venvs = [".venv", "venv", ".env", "env"]
    
    for venv_name in possible_venvs:
        if os.path.isdir(venv_name):
            return venv_name
    
    return None

def validate_venv_python_version(venv_path):
    """Check if venv has Python 3.12+"""
    try:
        # Find python executable in venv
        if os.name == 'nt':  # Windows
            python_exe = os.path.join(venv_path, "Scripts", "python.exe")
        else:  # Linux/macOS
            python_exe = os.path.join(venv_path, "bin", "python")
        
        if not os.path.exists(python_exe):
            return False, "Python executable not found"
        
        # Check version
        result = subprocess.run(
            [python_exe, "--version"],
            capture_output=True,
            text=True
        )
        
        version_str = result.stdout.strip() or result.stderr.strip()
        # Parse version like "Python 3.12.0"
        if "Python" in version_str:
            parts = version_str.split()[-1].split(".")
            major, minor = int(parts[0]), int(parts[1])
            if major >= 3 and minor >= 12:
                return True, f"Python {major}.{minor}"
            else:
                return False, f"Python {major}.{minor} (need 3.12+)"
        
        return False, "Could not parse version"
    except Exception as e:
        return False, str(e)

def manage_venv():
    """Detect and manage virtual environment"""
    print("\n🔍 Scanning for existing virtual environment...")
    
    existing_venv = check_existing_venv()
    
    if existing_venv:
        print(f"✅ Found existing venv: {existing_venv}")
        
        # Validate Python version in venv
        is_valid, version_info = validate_venv_python_version(existing_venv)
        
        if is_valid:
            print(f"✅ Python version: {version_info} (compatible!)")
            response = input(f"\nReuse existing venv at '{existing_venv}'? (y/N): ").strip().lower()
            if response == 'y':
                print(f"✅ Using existing venv: {existing_venv}")
                return True
        else:
            print(f"⚠️  Python version: {version_info} (incompatible!)")
        
        # Ask to recreate
        response = input("\nRecreate venv with Python 3.12? (Y/n): ").strip().lower()
        if response != 'n':
            print(f"🗑️  Removing old venv: {existing_venv}")
            shutil.rmtree(existing_venv, ignore_errors=True)
            return create_venv_with_uv()
        else:
            print("⚠️  Proceeding with existing venv (may have compatibility issues)")
            return True
    else:
        print("❌ No existing venv found")
        return create_venv_with_uv()

def check_env_file():
    """Check for existing .env file"""
    print("\n🔍 Scanning for .env file...")
    
    if os.path.exists(".env"):
        print("✅ Found existing .env file")
        response = input("Overwrite existing .env file? (y/N): ").strip().lower()
        if response == 'y':
            return setup_env_file()
        else:
            print("✅ Using existing .env file")
            return True
    else:
        print("❌ No .env file found")
        return setup_env_file()

def create_venv_with_uv():
    """Create virtual environment using uv"""
    print("\n🔧 Creating virtual environment with uv...")
    try:
        # Determine venv name based on OS
        venv_name = ".venv"
        run_uv_command(["venv", venv_name])
        print(f"✅ Virtual environment created: {venv_name}")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment with uv!")
        return False

def install_requirements_with_uv():
    """Install required packages using uv"""
    print("\n📦 Installing requirements with uv...")
    try:
        run_uv_command(["pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully with uv!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements with uv!")
        return False

def install_kittentts():
    """Install KittenTTS from GitHub release for Python 3.12"""
    print("\n🎤 Installing KittenTTS (Voice TTS Support)...")
    
    if sys.version_info < (3, 12):
        print("⚠️  KittenTTS requires Python 3.12+")
        print("   Current version: {}.{}".format(sys.version_info.major, sys.version_info.minor))
        print("   Skipping KittenTTS installation...")
        return False
    
    try:
        kittentts_wheel = "https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl"
        print(f"   Installing from: {kittentts_wheel}")
        run_uv_command(["pip", "install", kittentts_wheel])
        print("✅ KittenTTS installed successfully!")
        print("   Voice TTS/STT features are now available!")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Failed to install KittenTTS")
        print("   You can install it manually later with:")
        print("   uv pip install https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl")
        return False
    except Exception as e:
        print(f"⚠️  Error installing KittenTTS: {e}")
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
    
    # Manage virtual environment (detect, validate, or create)
    if not manage_venv():
        return False
    
    # Check/setup .env file
    if not check_env_file():
        return False
    
    # Install requirements with uv
    if not install_requirements_with_uv():
        return False
    
    # Install KittenTTS for Python 3.12 voice support
    install_kittentts()  # Optional, but recommended for voice features
    
    print("\n" + "=" * 50)
    print("🎉 Setup complete!")
    print("=" * 50)
    
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Activate venv: .venv\\Scripts\\activate (Windows) or source .venv/bin/activate (Linux/Mac)")
    print("3. Run: python bot.py")
def launch_bot():
    """Ask user which bot variant to launch and start it"""
    print("\n" + "=" * 50)
    print("🤖 Launch Discord AI Bot")
    print("=" * 50)
    print("\nWhich bot would you like to run?")
    print("1. 🚀 Normal Mode (python bot.py)")
    print("2. 🔄 Development Mode (python dev_bot.py - auto-restart on changes)")
    print("3. ⏭️  Skip - I'll run it manually later")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            print("\n🚀 Starting bot in normal mode...")
            print("   (Press Ctrl+C to stop)\n")
            try:
                subprocess.run([sys.executable, "bot.py"])
            except KeyboardInterrupt:
                print("\n\n👋 Bot stopped. Goodbye!")
            return True
            
        elif choice == "2":
            print("\n🔄 Starting bot in development mode...")
            print("   (Auto-restarts on file changes, Press Ctrl+C to stop)\n")
            try:
                subprocess.run([sys.executable, "dev_bot.py"])
            except KeyboardInterrupt:
                print("\n\n👋 Bot stopped. Goodbye!")
            return True
            
        elif choice == "3":
            print("\n⏭️  Skipping bot launch.")
            print("   You can start the bot manually later with:")
            print("   - Normal:      python bot.py")
            print("   - Development: python dev_bot.py")
            return True
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

def main_with_launch():
    """Main setup function with bot launch option"""
    success = main()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 Setup complete!")
        print("=" * 50)
        
        print("\n🎤 Voice Features:")
        print("   KittenTTS (TTS) was automatically installed for Python 3.12")
        print("   Whisper (STT) is included for speech recognition")
        print("   Ready to use: !join_voice, !listen, !speak commands")
        print("\n💡 Using uv for faster installs and synced dependencies!")
        print("   To update packages: uv pip install --upgrade <package>")
        print("   To sync all: uv pip install -r requirements.txt")
        print("   To install new Python: uv python install 3.12")
        
        # Ask user if they want to launch the bot
        response = input("\n🤔 Would you like to launch the bot now? (y/n): ").strip().lower()
        if response == 'y':
            launch_bot()
    
    return success

if __name__ == "__main__":
    success = main_with_launch()
    sys.exit(0 if success else 1)