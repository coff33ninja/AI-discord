#!/usr/bin/env python3
"""
Smart Setup Launcher
Automatically uses Python 3.12 if available, otherwise uses current Python
"""

import os
import sys
import subprocess
import shutil

def find_python_312():
    """Try to find Python 3.12 installation"""
    possible_paths = [
        "python3.12",
        "python3.12.exe",
        "py.exe -3.12",  # Windows Python Launcher
    ]
    
    # Check if uv has Python 3.12 installed
    if shutil.which("uv"):
        try:
            result = subprocess.run(
                ["uv", "python", "find", "3.12"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                python_path = result.stdout.strip().split('\n')[0]
                if os.path.exists(python_path):
                    return python_path
        except:
            pass
    
    # Check standard locations
    for python_cmd in possible_paths:
        if shutil.which(python_cmd):
            return python_cmd
    
    return None

def main():
    """Main launcher"""
    print("🚀 Discord AI Bot Setup Launcher")
    print("=" * 50)
    
    # Try to find Python 3.12
    python_312 = find_python_312()
    
    if python_312 and python_312 != sys.executable:
        print(f"✅ Found Python 3.12: {python_312}")
        print("🔄 Restarting setup.py with Python 3.12...\n")
        
        # Run setup.py with Python 3.12
        try:
            result = subprocess.run(
                [python_312, "setup.py"],
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            sys.exit(result.returncode)
        except Exception as e:
            print(f"❌ Error running Python 3.12: {e}")
            print("Falling back to current Python...")
    
    # Fall back to current Python
    if sys.version_info >= (3, 12):
        print(f"✅ Using Python {sys.version_info.major}.{sys.version_info.minor}")
        print("🔄 Running setup.py...\n")
        
        # Import and run setup
        import setup
        success = setup.main_with_launch()
        sys.exit(0 if success else 1)
    else:
        print(f"❌ Python 3.12 not found, current version: {sys.version_info.major}.{sys.version_info.minor}")
        print("\n💡 Try one of these:")
        print("   1. Restart your terminal (uv installed Python 3.12)")
        print("   2. Run: python3.12 setup.py")
        print("   3. Run: uv python install 3.12")
        sys.exit(1)

if __name__ == "__main__":
    main()
