# Python 3.12 Setup Quick Reference

## ⚡ Quick Start (UV - Fastest)

```bash
# 1. Install Python 3.12
uv python install 3.12
uv python pin 3.12

# 2. Create environment and install
uv venv
uv pip install -r requirements.txt

# 3. Install KittenTTS (separate step)
uv pip install https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl

# 4. Setup
python setup.py

# 5. Run
python bot.py              # Standard
python dev_bot.py          # With auto-reload
```

## ✅ Version Requirements

| Component | Version | Required | Recommended |
|-----------|---------|----------|-------------|
| **Python** | 3.12.x | Yes | YES ← Use this |
| Python | 3.13+ | No | ⚠️ Threading issues |
| Python | 3.10-3.11 | No | Works, but older |

## 🔧 Installation Methods

### Option 1: UV (RECOMMENDED - FASTEST)
```bash
uv python install 3.12
uv venv
uv pip install -r requirements.txt
uv pip install https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl
```

### Option 2: PIP (Standard)
```bash
python -m venv .venv
.venv\Scripts\activate           # Windows
source .venv/bin/activate        # Linux/Mac
pip install -r requirements.txt
pip install https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl
```

## 📋 Package Versions

**Core:**
- discord.py 2.5.2
- google-generativeai 0.7.0
- python-dotenv 1.0.1

**Web:**
- aiohttp 3.12.14
- requests 2.32.4
- beautifulsoup4 4.12.3

**Database:**
- aiosqlite 1.3.0

**Search:**
- duckduckgo-search 3.9.2

**Voice:**
- KittenTTS 0.1.0 (from wheel)
- openai-whisper 20250623
- spacy 3.8.7
- soundfile 0.12.1
- numpy 1.26.4

**Dev:**
- watchdog 6.0.0 (Python 3.12 ONLY)

## 🐛 If You See Errors

### "TypeError: 'handle' must be a _ThreadHandle"
→ You have Python 3.13, switch to 3.12:
```bash
uv python install 3.12
uv python pin 3.12
```

### "Could not find a version that satisfies..."
→ For KittenTTS, use the wheel URL (don't try `pip install kittentts`):
```bash
pip install https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl
```

### "ImportError: cannot import name 'Content'"
→ google-generativeai needs updating on Python 3.12:
```bash
pip install --upgrade google-generativeai
```

## ✔️ Verify Installation

```bash
# Check Python version
python --version              # Should be 3.12.x

# Check packages installed
pip list

# Check specific packages
pip show discord.py
pip show google-generativeai

# Try importing
python -c "import discord; import google.generativeai; print('✅ All good!')"
```

## 📖 Full Documentation

See `docs/PYTHON_COMPATIBILITY.md` for:
- Detailed version compatibility matrix
- Troubleshooting guide
- Development notes
- Additional resources

## 💡 Pro Tips

1. **Always use Python 3.12.x** - Most stable for all features
2. **Use UV** - Significantly faster than pip
3. **KittenTTS from wheel** - Don't try to install from PyPI
4. **dev_bot.py requires Python 3.12** - For watchdog auto-reload
5. **bot.py works on Python 3.10+** - But 3.12 recommended

## 🚀 Running the Bot

```bash
# Standard run
python bot.py

# Development (auto-restart on file changes)
python dev_bot.py

# Windows batch file
run_bot.bat
dev_bot.bat
```
