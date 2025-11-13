# Installation & Setup

The bot uses **setup.py** to handle all installation requirements including:
- ✅ Python version management (3.10+)
- ✅ Virtual environment (venv) setup
- ✅ UV package manager integration
- ✅ Dependency installation
- ✅ Requirements validation

## Quick Start

Simply run the setup script:

```bash
python setup.py
```

This will:
1. Create a virtual environment (`.venv/`)
2. Install UV if needed
3. Install all dependencies from `requirements.txt`
4. Validate Python version compatibility
5. Verify all modules are installed correctly

## What's Installed

See [`requirements.txt`](../../requirements.txt) for the complete list of packages and their pinned versions, optimized for **Python 3.10-3.12**.

## Running the Bot

After setup completes:

```bash
# Activate virtual environment (if not auto-activated)
source .venv/Scripts/activate  # Windows
source .venv/bin/activate       # macOS/Linux

# Run the bot
python bot.py

# Or development mode with auto-restart
python dev_bot.py
```

## Troubleshooting

If you encounter setup issues:

1. **Python version** - Ensure you have Python 3.10 or higher: `python --version`
2. **Virtual environment** - Delete `.venv/` and rerun `python setup.py`
3. **Dependencies** - Run `python setup.py` again to reinstall all packages
4. **Permission errors** - Run terminal as administrator

## Manual Setup (Advanced)

If you prefer manual setup:

```bash
# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

For more details on specific modules, see the individual documentation in `/docs/modules/`.
