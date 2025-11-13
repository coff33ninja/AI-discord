# Python & Dependencies Compatibility Guide

## Python Version Recommendations

### ✅ RECOMMENDED: Python 3.12.x
- **All features fully supported**
- **All dependencies tested and verified**
- **Best stability and performance**
- **Voice TTS/STT fully functional**
- **File watching (dev_bot.py) works perfectly**

### ⚠️ NOT RECOMMENDED: Python 3.13+
- ❌ watchdog has threading compatibility issues
- ❌ KittenTTS may have installation/runtime issues
- ⚠️ Some async operations may behave unexpectedly
- Consider using 3.12 until dependencies are updated

### ✅ COMPATIBLE: Python 3.10-3.11
- Most features work, but not fully tested
- Some newer async features may not work optimally
- Recommended to upgrade to 3.12 for best experience

### ❌ NOT SUPPORTED: Python < 3.10
- Discord.py 2.5.2 requires Python 3.8+
- Some dependencies require Python 3.9+
- **Upgrade to Python 3.12 for this bot**

---

## Installing Python 3.12 with UV

### Using UV (Recommended - Fastest)

```bash
# Install or upgrade UV first
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Python 3.12
uv python install 3.12

# Set as active Python
uv python pin 3.12
```

### Manual Installation

1. Visit [python.org](https://www.python.org/downloads/)
2. Download Python 3.12.x for your OS
3. Install and ensure "Add to PATH" is checked
4. Verify: `python --version`

### Check Current Python Version

```bash
python --version
python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
```

---

## Dependency Compatibility Matrix

| Package | Version | Python 3.10 | Python 3.12 | Python 3.13 | Notes |
|---------|---------|:-----------:|:-----------:|:-----------:|-------|
| discord.py | 2.5.2 | ✅ | ✅ | ✅ | Core dependency |
| google-generativeai | 0.7.0 | ✅ | ✅ | ⚠️ | Gemini API |
| aiohttp | 3.12.14 | ✅ | ✅ | ✅ | HTTP client |
| requests | 2.32.4 | ✅ | ✅ | ✅ | HTTP requests |
| beautifulsoup4 | 4.12.3 | ✅ | ✅ | ✅ | Web parsing |
| aiosqlite | 1.3.0 | ✅ | ✅ | ✅ | Database |
| duckduckgo-search | 3.9.2 | ✅ | ✅ | ✅ | Web search |
| **watchdog** | **6.0.0** | ⚠️ | ✅ | ❌ | **Threading issues on 3.13** |
| spacy | 3.8.7 | ✅ | ✅ | ✅ | NLP |
| numpy | 1.26.4 | ✅ | ✅ | ✅ | Numerical |
| openai-whisper | 20250623 | ✅ | ✅ | ⚠️ | Speech-to-text |
| KittenTTS | 0.1.0 | ⚠️ | ✅ | ⚠️ | Text-to-speech |

Legend: ✅ = Full support | ⚠️ = Partial/untested | ❌ = Not supported

---

## Installation Instructions

### Using UV (FASTEST - RECOMMENDED)

```bash
# 1. Ensure Python 3.12 is active
uv python show  # Should show Python 3.12.x

# 2. Create virtual environment
uv venv

# 3. Install all dependencies
uv pip install -r requirements.txt

# 4. Install KittenTTS from wheel (manually)
uv pip install https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl

# 5. Run setup.py
python setup.py
```

### Using PIP (Standard)

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate

# 3. Install requirements
pip install -r requirements.txt

# 4. Install KittenTTS from wheel
pip install https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl

# 5. Run setup
python setup.py
```

---

## Troubleshooting Compatibility Issues

### Python 3.13: watchdog threading error
```
TypeError: 'handle' must be a _ThreadHandle
```

**Solution:** Downgrade to Python 3.12
```bash
uv python install 3.12
uv python pin 3.12
```

### KittenTTS installation fails
```
ERROR: Could not find a version that satisfies...
```

**Solution:** Install from wheel, not from pip
```bash
pip install https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl
```

### google-generativeai import errors
```
ImportError: cannot import name 'Content' from 'google.generativeai'
```

**Solution:** Use Python 3.12 and latest version
```bash
pip install --upgrade google-generativeai
```

### Whisper speech recognition not working
```
ModuleNotFoundError: No module named 'whisper'
```

**Solution:** Install with explicit version
```bash
pip install openai-whisper==20250623
```

---

## Version Pinning Strategy

We use specific version pinning in `requirements.txt` to ensure:

1. **Stability** - Known good versions that work together
2. **Consistency** - Same environment across all installations
3. **Compatibility** - All packages work with Python 3.12.x
4. **Reproducibility** - No surprise breaking changes

### To upgrade a single package safely:

```bash
# Using UV
uv pip install --upgrade package_name

# Using PIP
pip install --upgrade package_name

# Then update requirements.txt version number
```

---

## Checking Package Compatibility

### For specific package versions:

```bash
# Check PyPI page
pip index versions package_name

# Check package info
pip show package_name

# Check if compatible with current Python
pip install --dry-run package_name
```

### For all installed packages:

```bash
pip list
pip freeze
uv pip freeze
```

---

## Development Notes

### Using dev_bot.py (auto-reload)

The `dev_bot.py` file uses `watchdog` for file monitoring. It requires:

- ✅ Python 3.12.x (or 3.10-3.11)
- ✅ watchdog 6.0.0
- ✅ Working file system (local drives, not network mounts)

**NOT compatible with Python 3.13** due to threading changes.

### Using bot.py (standard run)

Works with any supported Python version:
- ✅ No dependencies on watchdog
- ✅ Compatible with Python 3.10+
- ✅ Compatible with Python 3.13

```bash
python bot.py
```

---

## Summary

| Task | Recommended | Notes |
|------|-------------|-------|
| **New Installation** | Python 3.12.x | Use `uv python install 3.12` |
| **Using dev_bot.py** | Python 3.12.x | Required for watchdog |
| **Using bot.py** | Python 3.10+ | Works with any version |
| **Production Deployment** | Python 3.12.x | Most stable and tested |
| **Troubleshooting** | Python 3.12.x | Downgrade from 3.13 if issues |

---

## Additional Resources

- [Python Downloads](https://www.python.org/downloads/) - Official Python releases
- [UV Documentation](https://docs.astral.sh/uv/) - UV package manager
- [Discord.py Requirements](https://discordpy.readthedocs.io/) - Discord.py docs
- [PyPI Packages](https://pypi.org/) - Package version history
