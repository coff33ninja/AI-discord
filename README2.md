# Tsundere AI Discord Bot 🤖💕

A Discord bot with a classic tsundere personality powered by Google's Gemini AI. She's helpful but acts annoyed about it, uses mild swearing, and gets adorably flustered when complimented!

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Discord.py](https://img.shields.io/badge/discord.py-2.3.2-blue.svg)
![Gemini AI](https://img.shields.io/badge/Gemini-2.5--flash-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- 🧠 **AI Chat** - Google Gemini 2.5 Flash with conversation memory
- 🔍 **Web Search** - DuckDuckGo integration with instant answers
- 🎮 **Games** - Number Guess, RPS, Trivia, Magic 8-Ball
- 💝 **Relationships** - Tracks interaction history with personalized responses
- 💬 **Memory** - Remembers conversations for context-aware replies
- ⏰ **Reminders** - Natural language reminders and daily subscriptions
- 🛠️ **Server Management** - Role/channel creation, user moderation
- 🎤 **Voice** - Speech-to-text and text-to-speech support

**[📖 Full Documentation](./docs/)** | **[🎯 Commands](./docs/commands.md)** | **[📦 Modules](./docs/MODULES.md)**

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- [Discord Bot Token](https://discord.com/developers/applications)
- [Google Gemini API Key](https://makersuite.google.com/app/apikey)

### Installation

```bash
# Clone repository
git clone https://github.com/coff33ninja/AI-discord.git
cd AI-discord

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "DISCORD_BOT_TOKEN=your_token_here" > .env
echo "GEMINI_API_KEY=your_key_here" >> .env

# Run bot
python bot.py
```

**📚 [Full Setup Guide](./docs/setup/)**

## 📖 Documentation

Everything is documented in `/docs/`:

| Resource | Purpose |
|----------|---------|
| **[commands.md](./docs/commands.md)** | All 47+ commands with examples |
| **[MODULES.md](./docs/MODULES.md)** | Index of 22 modules |
| **[modules/](./docs/modules/)** | Detailed module documentation |
| **[voice/](./docs/voice/)** | Voice & TTS setup |
| **[setup/](./docs/setup/)** | Installation guides |

**[👉 Start here: Documentation Hub](./docs/)**

## 🎯 Quick Commands

| Category | Examples |
|----------|----------|
| **AI** | `!ai <question>` • `!mood` • `!relationship` |
| **Games** | `!game guess` • `!rps rock` • `!8ball <question>` • `!trivia` |
| **Search** | `!search <query>` |
| **Utilities** | `!time` • `!weather <city>` • `!fact` • `!joke` |
| **Reminders** | `!remind in 5 minutes to <message>` |
| **Server** | `!create_role <name>` • `!create_channel <name>` |
| **Voice** | `!join_voice` • `!listen` • `!speak <text>` |

**[📋 Full Commands List](./docs/commands.md)**

## 🎨 Customization

Customize the bot's personality in `persona_card.json`:
- Bot name
- Response templates
- Speech patterns
- Personality traits
- Relationship-specific responses

Use `!reload_persona` to apply changes without restarting.

## 🔧 Project Structure

```
AI-discord/
├── bot.py                      # Main bot application
├── dev_bot.py                  # Auto-restart development runner
├── .env                        # Environment variables
├── persona_card.json           # Bot personality & name
├── requirements.txt            # Dependencies
├── docs/                       # 📖 Complete documentation
├── data/                       # Database storage (auto-created)
└── modules/                    # 22 feature modules
    ├── ai_database.py          # Async database
    ├── api_manager.py          # Gemini API with key rotation
    ├── search.py               # Web search
    ├── games.py                # Game implementations
    ├── social.py               # Relationship tracking
    ├── time_utilities.py       # Reminders & scheduling
    ├── server_actions.py       # Role/channel management
    ├── response_handler.py     # Message formatting
    ├── knowledge_manager.py    # Custom knowledge base
    ├── persona_manager.py      # Personality system
    ├── personality.py          # Traits & mood
    ├── config_manager.py       # Configuration
    ├── utilities.py            # Helper functions
    ├── logger.py               # Logging setup
    ├── bot_name_service.py     # Name management
    └── voice_*.py              # Voice modules (TTS/STT)
```

## 📚 Running the Bot

```bash
# Simple run
python bot.py

# Development mode (auto-restart on file changes)
python dev_bot.py

# Windows batch scripts
run_bot.bat
dev_bot.bat
```

**Stop with:** `Ctrl+C` or `!shutdown` command

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Bot not responding | Check Discord token and bot permissions |
| AI not working | Verify Gemini API key is correct |
| API rate limits | Add backup API keys to `.env` |
| Search not working | Check internet connectivity |
| Permission errors | Ensure bot has required Discord permissions |

## 💝 Relationship System

The bot remembers users and builds relationships:

| Level | Interactions | Behavior |
|-------|-------------|----------|
| **Stranger** | 0-4 | Very cold and tsundere |
| **Acquaintance** | 5-19 | Slightly warmer but defensive |
| **Friend** | 20-49 | More caring, still denies it |
| **Close Friend** | 50+ | Very caring, extremely flustered |

## 🤝 Contributing

Contributions welcome! Feel free to submit a Pull Request.

## 📄 License

MIT License - See [LICENSE](LICENSE)

## 🙏 Credits

- **Google Gemini AI** - Intelligent conversations
- **Discord.py** - Discord API wrapper
- **DuckDuckGo** - Web search
- **OpenAI Whisper** - Speech recognition
- **KittenTTS** - Text-to-speech

---

*"I-it's not like I wanted you to star this repository or anything, baka!"* - Your Tsundere Bot 💕
