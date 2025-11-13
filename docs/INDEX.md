# Documentation Index

Quick navigation for all bot documentation.

## 🚀 Getting Started

- **[README.md](../README.md)** - Main project page, features, quick start
- **[Commands Reference](./commands.md)** - All `!` commands with examples
- **[Setup Guides](./setup/)** - Installation and configuration

## 📚 Documentation by Category

### User Documentation
- **[Commands Reference](./commands.md)** - Every command explained
  - AI & Chat commands
  - Games and utilities
  - Voice commands
  - Admin commands
- **[Setup Guides](./setup/)** - Getting started
  - Installation
  - Configuration
  - API key setup

### Developer Documentation
- **[Modules Overview](./MODULES.md)** - All modules at a glance
- **[Module Documentation](./modules/)** - Detailed module docs
  - [api_manager.py](./modules/api_manager.md) - Gemini AI integration
  - [ai_database.py](./modules/ai_database.md) - Data persistence
  - [search.py](./modules/search.md) - Web search
  - [games.py](./modules/games.md) - Game implementations
  - [social.py](./modules/social.md) - User relationships
  - And more...

### Feature Documentation
- **[Voice Integration](./voice/)** - Voice chat with AI
  - [Complete Guide](./voice/stt_tts_complete.md)
  - [TTS Documentation](./voice/tts.md)
  - [Integration Guide](./voice/integration.md)

### Status & Progress
- **[Documentation Status](./STATUS.md)** - What's documented and what's next

## 🎯 Find What You Need

### "How do I...?"
| Question | Answer |
|----------|--------|
| Use a command? | → [Commands Reference](./commands.md) |
| Install the bot? | → [Setup Guides](./setup/) |
| Understand a module? | → [Modules Overview](./MODULES.md) |
| Use voice features? | → [Voice Integration](./voice/) |
| Set up the database? | → [ai_database.py](./modules/ai_database.md) |
| Search the web? | → [search.py](./modules/search.md) |
| Create games? | → [games.py](./modules/games.md) |
| Track relationships? | → [social.py](./modules/social.md) |

### By Experience Level

**Beginner (Just started)**
1. Read [README.md](../README.md)
2. Follow [Setup Guides](./setup/)
3. Check [Commands Reference](./commands.md)

**Intermediate (Using the bot)**
1. Review [Commands Reference](./commands.md)
2. Explore voice features in [Voice Integration](./voice/)
3. Check [Documentation Status](./STATUS.md) for feature updates

**Advanced (Contributing/Developing)**
1. Start with [Modules Overview](./MODULES.md)
2. Read specific module documentation
3. Check Python docstrings in source code
4. Review implementation in `bot.py`

## 📖 All Available Documents

### Root
- `README.md` - Project overview
- `requirements.txt` - Dependencies
- `bot.py` - Main bot code

### `/docs`
```
docs/
├── INDEX.md (this file)
├── STATUS.md - Documentation progress
├── commands.md - All commands
├── MODULES.md - Module index
├── modules/
│   ├── api_manager.md ✅
│   ├── ai_database.md ✅
│   ├── search.md (pending)
│   ├── games.py (pending)
│   ├── social.md (pending)
│   └── ... (13+ modules total)
├── voice/
│   ├── stt_tts_complete.md ✅
│   ├── tts.md ✅
│   └── integration.md ✅
└── setup/
    └── tts_setup.md ✅
```

## 🔗 Quick Links

### Commands by Category
- [AI & Chat](./commands.md#-ai--chat-commands)
- [Search & Info](./commands.md#-search--information-commands)
- [Utilities](./commands.md#-utility-commands)
- [Games](./commands.md#-game-commands)
- [Server Management](./commands.md#-server-management-commands)
- [Time & Reminders](./commands.md#-time--reminder-commands)
- [Voice](./commands.md#-voice-interaction-commands)
- [Admin](./commands.md#-admin-commands)

### Modules by Type
- **Core**: [api_manager](./modules/api_manager.md), [ai_database](./modules/ai_database.md)
- **Features**: search, games, social, time_utilities, server_actions
- **Voice**: stt_manager, tts_manager, voice_channel, ai_voice_integration
- **Config**: persona_manager, personality, config_manager
- **Utils**: utilities, logger, response_handler, bot_name_service

## 🆘 Troubleshooting

### "I can't find documentation for..."
1. Check [Modules Overview](./MODULES.md)
2. Check [Documentation Status](./STATUS.md)
3. Look at Python docstrings in source code
4. Search in `/docs` folder

### "The documentation is unclear"
1. Check the Python source docstrings
2. Look for examples in `bot.py`
3. Check module examples in the docs
4. Review test code or examples

### "Something isn't working"
1. Check [Commands Reference](./commands.md)
2. Review module-specific troubleshooting
3. Check error messages in logs
4. Review configuration in `.env` file

## 📝 How to Read This Documentation

### Command Documentation
- **Command** - The `!` command to use
- **Aliases** - Shorter versions of the command
- **Usage** - Example of how to use it
- **Description** - What it does

Example:
```
| `!ai <question>` | `!ask`, `!chat` | `!ai What is AI?` | Ask the AI anything |
```

### Module Documentation
Each module includes:
- Overview of what it does
- Key classes and functions
- Detailed function reference
- Usage examples
- Configuration options
- Dependencies

Example structure:
```
# module_name Module

## Overview
What it does

## Key Classes
Main classes

## Main Functions
Functions with parameters, returns, examples

## Configuration
Settings

## Usage Examples
Real code examples
```

## 🎓 Learning Path

### If you want to...

**Understand the bot's architecture:**
1. Read [README.md](../README.md)
2. Review [Modules Overview](./MODULES.md)
3. Check [Commands Reference](./commands.md)

**Add a new command:**
1. Check [commands.md](./commands.md)
2. Review relevant module docs
3. Follow pattern in `bot.py`
4. Update `commands.md` with new command

**Understand data flow:**
1. Read [api_manager.md](./modules/api_manager.md)
2. Read [ai_database.md](./modules/ai_database.md)
3. Check how they're used in `bot.py`

**Work with voice:**
1. Read [Voice Integration](./voice/integration.md)
2. Check [stt_tts_complete.md](./voice/stt_tts_complete.md)
3. Review voice module docs

## 📞 Support Resources

- **Python Docs** - `help(module_name)` in Python
- **IDE Tooltips** - Hover over functions/classes
- **Source Comments** - Read docstrings in code
- **Examples** - Check `bot.py` for usage patterns

## ✅ Checklist for Using This Documentation

- [ ] Found what you're looking for
- [ ] Documentation was clear
- [ ] Examples worked
- [ ] Understood the concepts
- [ ] Ready to use/develop

*If any checkbox is unchecked, check troubleshooting above or review the source docstrings.*

---

**Need something?** Start with [Modules Overview](./MODULES.md) or [Commands Reference](./commands.md)!

*Last Updated: 2025-11-14*
