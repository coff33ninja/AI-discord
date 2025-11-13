# 🔧 Compatibility Matrix - Python & Dependencies

Complete compatibility guide for AI Discord Bot with Python versions and UV package manager.

## 📋 Quick Summary

| Component | Recommended | Minimum | Maximum | Status |
|-----------|-------------|---------|---------|--------|
| **Python** | 3.10-3.12 | 3.8 | 3.13 ⚠️ | ✅ |
| **UV Package Manager** | 0.4+ | 0.3 | Latest | ✅ |
| **KittenTTS** | 0.1.0 | 0.1.0 | 0.1.0 | ⚠️ Preview |
| **discord.py** | 2.6+ | 2.3+ | 2.6.4 | ✅ |
| **watchdog** | 6.0.0 | 2.1+ | 6.0.0 | ✅ |

---

## 🐍 Python Versions

### **Recommended: Python 3.10 - 3.12**
Best compatibility for all dependencies. Most stable and tested.

```bash
# Install with uv
uv python install 3.12.0
# or
uv python install 3.10.14
```

### **Python 3.8 - 3.9**
Supported but older. May have minor compatibility issues with newer libraries.

```bash
uv python install 3.9.19
```

### **Python 3.13** ⚠️ **EXPERIMENTAL**
**Known Issue**: `watchdog` library has threading compatibility problems with Python 3.13.5

**Solution**: Use Python 3.12.x instead OR disable file watching in dev_bot.py

```bash
# Not recommended, use 3.12 instead
uv python install 3.12.4
```

---

## 📦 Dependencies & Compatibility

### **Discord.py** - Discord API Wrapper
- **Latest**: 2.6.4 ✅
- **Required**: ≥ 2.3.2
- **Python Support**: 3.8 - 3.12
- **Note**: discord.py 2.6.4 officially supports up to Python 3.12

```bash
uv pip install discord.py==2.6.4
```

### **KittenTTS** - Text-to-Speech
- **Latest**: 0.1.0 (Preview)
- **Python Support**: 3.8+
- **Note**: Still in preview, may have issues with newest Python versions

```bash
uv pip install https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl
```

**Dependencies**:
- `spacy` ≥ 3.0
- `num2words` ≥ 0.5
- `espeakng_loader` ≥ 0.2

### **Watchdog** - File System Monitoring
- **Latest**: 6.0.0 (Nov 2024) ✅
- **For dev_bot.py**: Requires watchdog
- **Python Support**: 3.8+
- **Python 3.13 Issue**: ⚠️ Threading compatibility problem

```bash
# Latest compatible version
uv pip install watchdog==6.0.0

# For Python 3.13 workaround: don't use dev_bot.py or downgrade Python
```

**Alternative for Python 3.13**:
- Use `python bot.py` directly (no file watching)
- Downgrade to Python 3.12
- Fix dev_bot.py to use asyncio instead of threading

### **Google Gemini API** - AI Engine
- **Library**: `google-generativeai`
- **Latest Tested**: 0.3+
- **Python Support**: 3.8+

```bash
uv pip install google-generativeai>=0.3
```

### **Web Search** - DuckDuckGo
- **Library**: `duckduckgo-search`
- **Python Support**: 3.8+

```bash
uv pip install duckduckgo-search
```

### **Database** - SQLite
- **Library**: `aiosqlite`
- **Latest**: 1.3.0+
- **Python Support**: 3.8+

```bash
uv pip install aiosqlite
```

### **Voice Features** - OpenAI Whisper
- **Library**: `openai-whisper`
- **Python Support**: 3.8+

```bash
uv pip install openai-whisper
```

---

## 🎯 Recommended Setup with UV

### **Option 1: Python 3.12 (Recommended)**
Best overall compatibility, all features work.

```bash
# Install Python 3.12
uv python install 3.12.4

# Create virtual environment
uv venv --python 3.12.4

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install all dependencies
uv pip install -r requirements.txt

# All features work: dev_bot.py, bot.py, voice, everything ✅
python dev_bot.py
```

### **Option 2: Python 3.10 (Stable Alternative)**
Proven compatibility, all features work.

```bash
uv python install 3.10.14
uv venv --python 3.10.14
source .venv/bin/activate
uv pip install -r requirements.txt
python dev_bot.py
```

### **Option 3: Python 3.13 (Not Recommended Yet)**
Experimental, has watchdog issues.

```bash
uv python install 3.13.5
uv venv --python 3.13.5
source .venv/bin/activate
uv pip install -r requirements.txt

# PROBLEM: dev_bot.py won't work
# SOLUTION: Use regular bot.py without file watching
python bot.py

# OR fix dev_bot.py to use asyncio instead of threading
```

---

## ⚙️ UV Commands Reference

```bash
# List installed Python versions
uv python list

# Install specific Python version
uv python install 3.12.4

# Create virtual environment with specific Python
uv venv --python 3.12.4

# Upgrade all packages
uv pip install --upgrade -r requirements.txt

# Check for dependency conflicts
uv pip compile requirements.txt

# Sync exact versions from lock file
uv sync
```

---

## 🚀 Installation Steps Using UV

```bash
# 1. Install uv (if not already installed)
# Windows: winget install uv
# macOS: brew install uv
# Linux: curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install Python 3.12
uv python install 3.12.4

# 3. Clone and navigate to project
git clone https://github.com/coff33ninja/AI-discord.git
cd AI-discord

# 4. Create virtual environment
uv venv --python 3.12.4

# 5. Activate (varies by OS/shell)
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows cmd:
.venv\Scripts\activate.bat
# macOS/Linux:
source .venv/bin/activate

# 6. Install dependencies with UV
uv pip install -r requirements.txt

# 7. Create .env file
cp .env.example .env  # or create manually
# Edit .env with your API keys:
# DISCORD_BOT_TOKEN=...
# GEMINI_API_KEY=...

# 8. Run the bot
python bot.py

# 9. Or use dev mode (file watching)
python dev_bot.py
```

---

## 🔍 Troubleshooting

### Issue: "TypeError: 'handle' must be a _ThreadHandle" in dev_bot.py

**Cause**: Python 3.13.5 has threading API changes that break watchdog

**Solutions**:
1. ✅ **Downgrade Python** (Recommended):
   ```bash
   uv python install 3.12.4
   uv venv --python 3.12.4
   ```

2. Use regular bot without file watching:
   ```bash
   python bot.py  # No auto-restart, but works fine
   ```

3. Fix dev_bot.py (Advanced):
   Replace threading with asyncio for watching

### Issue: "No module named 'kittentts'"

**Solution**:
```bash
uv pip install https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl
```

### Issue: "discord.py not compatible"

**Solution**:
```bash
# Ensure correct version
uv pip install discord.py==2.6.4 --force-reinstall

# Check installation
python -c "import discord; print(discord.__version__)"
```

### Issue: "Watchdog crashes on Python 3.13"

**Solution**: Downgrade Python to 3.12
```bash
uv python uninstall 3.13.5
uv python install 3.12.4
```

---

## 📊 Full Dependency Tree

```
AI-Discord-Bot/
├── Python 3.10-3.12 (Recommended 3.12)
├── discord.py 2.6.4
├── google-generativeai 0.3+
├── duckduckgo-search
├── aiosqlite 1.3+
├── openai-whisper
├── KittenTTS 0.1.0
│   ├── spacy 3.8+
│   ├── num2words 0.5+
│   └── espeakng_loader 0.2+
├── watchdog 6.0.0 (Not needed for Python 3.13)
│   └── ⚠️ Skip if using Python 3.13
└── python-dotenv
```

---

## ✅ Verification Checklist

After installation, verify everything works:

```bash
# Check Python version
python --version
# Expected: Python 3.10.x, 3.11.x, or 3.12.x

# Check discord.py
python -c "import discord; print(f'discord.py {discord.__version__}')"
# Expected: discord.py 2.6.4

# Check KittenTTS
python -c "import kittentts; print('KittenTTS installed')"
# Expected: KittenTTS installed

# Check watchdog (unless Python 3.13)
python -c "import watchdog; print('watchdog installed')"
# Expected: watchdog installed

# Test bot imports
python -c "from modules import api_manager; print('Modules OK')"
# Expected: Modules OK

# Try running dev_bot
python dev_bot.py
# Should see: "🚀 Discord AI Bot Development Runner"
# If Python 3.13: Use 'python bot.py' instead
```

---

## 🎓 Understanding UV

UV is a modern, fast Python package manager written in Rust:

**Advantages over pip**:
- ✅ 10-100x faster than pip
- ✅ Manages Python versions
- ✅ Built-in virtual environment support
- ✅ Better dependency resolution
- ✅ Lock file support for reproducibility

**Basic UV Workflow**:
```bash
# Install packages
uv pip install package-name

# Install from requirements
uv pip install -r requirements.txt

# Manage Python versions
uv python install 3.12.4

# Create venv
uv venv --python 3.12.4

# Sync environment
uv sync
```

---

## 📚 Additional Resources

- [UV Documentation](https://docs.astral.sh/uv/)
- [discord.py Docs](https://discordpy.readthedocs.io/)
- [KittenTTS GitHub](https://github.com/KittenML/KittenTTS)
- [Python 3.13 Release Notes](https://docs.python.org/3.13/whatsnew/3.13.html)
- [Watchdog Documentation](https://watchdog.readthedocs.io/)

---

**Last Updated**: November 14, 2025  
**Status**: Verified with Python 3.10, 3.11, 3.12 ✅  
**Note**: Python 3.13 support pending watchdog fix
