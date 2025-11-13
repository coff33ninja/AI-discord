#!/usr/bin/env python3
"""
KittenTTS Setup Verification Script
Run this to verify all dependencies are properly installed
"""

import sys
import subprocess
from pathlib import Path


def check_package(package_name: str, import_name: str = None) -> bool:
    """Check if a package is installed."""
    import_name = import_name or package_name
    try:
        __import__(import_name)
        print(f"✓ {package_name} is installed")
        return True
    except ImportError:
        print(f"✗ {package_name} is NOT installed")
        return False


def check_command(cmd: str) -> bool:
    """Check if a command is available in PATH."""
    try:
        subprocess.run([cmd, '--version'], 
                      capture_output=True, 
                      timeout=5,
                      check=False)
        print(f"✓ {cmd} is available in PATH")
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print(f"✗ {cmd} is NOT available in PATH")
        return False


def main():
    print("=" * 60)
    print("KittenTTS Voice Integration - Setup Verification")
    print("=" * 60)
    print()

    all_good = True

    # Check Python packages
    print("Checking Python packages...")
    packages = [
        ('discord.py', 'discord'),
        ('google-generativeai', 'google'),
        ('python-dotenv', 'dotenv'),
        ('aiohttp', 'aiohttp'),
        ('requests', 'requests'),
        ('beautifulsoup4', 'bs4'),
        ('aiosqlite', 'aiosqlite'),
        ('soundfile', 'soundfile'),
        ('numpy', 'numpy'),
        ('kittentts', 'kittentts'),
    ]

    for package, import_name in packages:
        if not check_package(package, import_name):
            all_good = False

    print()
    print("Checking system commands...")
    commands = ['ffmpeg', 'ffprobe']

    for cmd in commands:
        if not check_command(cmd):
            all_good = False

    print()
    print("Checking module files...")
    modules = [
        'modules/tts_manager.py',
        'modules/voice_channel.py',
        'modules/voice_examples.py',
    ]

    for module in modules:
        path = Path(module)
        if path.exists():
            print(f"✓ {module} exists")
        else:
            print(f"✗ {module} NOT found")
            all_good = False

    print()
    print("=" * 60)

    if all_good:
        print("✓ All checks passed! You're ready to use KittenTTS!")
        return 0
    else:
        print("✗ Some checks failed. See instructions above.")
        print()
        print("Installation steps:")
        print("1. Install KittenTTS wheel:")
        print("   pip install https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl")
        print()
        print("2. Install other dependencies:")
        print("   pip install -r requirements.txt")
        print()
        print("3. Install FFmpeg:")
        print("   Windows (winget): winget install FFmpeg")
        print("   macOS (brew): brew install ffmpeg")
        print("   Linux (apt): sudo apt-get install ffmpeg")
        return 1


if __name__ == '__main__':
    sys.exit(main())
