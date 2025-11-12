# Coffee - Tsundere AI Discord Bot 🤖💕

A Discord bot with a classic tsundere personality powered by Google's Gemini AI. Meet Coffee - she's helpful but acts annoyed about it, uses mild swearing, and gets adorably flustered when complimented!

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Discord.py](https://img.shields.io/badge/discord.py-2.3.2-blue.svg)
![Gemini AI](https://img.shields.io/badge/Gemini-2.5--flash-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🎭 Personality

Coffee has a classic tsundere personality:
- **Reluctant Helper**: Acts annoyed while being genuinely helpful
- **Defensive**: Gets flustered easily, especially with compliments
- **Caring but Denying**: Obviously cares but refuses to admit it
- **Mild Attitude**: Uses "baka," "idiot," and mild swearing when frustrated
- **Relationship Growth**: Becomes more caring (but more flustered) as you interact more

## ✨ Features

### 🧠 **AI Integration**
- **Google Gemini 2.5 Flash** for intelligent conversations
- **Persona-driven responses** with consistent tsundere personality
- **Context-aware** responses based on relationship level
- **Timeout protection** for API calls (30-second limit)
- **🆕 Multiple API Keys** - Automatic rotation for better reliability
- **🆕 Rate Limit Handling** - Smart cooldown and retry logic

### 🔍 **🆕 Web Search**
- **DuckDuckGo Integration** - Search the web with tsundere attitude
- **Instant Answers** - Quick facts, calculations, and definitions
- **Smart Parsing** - BeautifulSoup-powered result extraction
- **Dual Methods** - API + HTML parsing for comprehensive results

### 🎮 **Interactive Games**
- **Number Guessing** with hints and attempt tracking
- **Rock Paper Scissors** with tsundere reactions
- **Trivia Games** with 30-second time limits
- **Magic 8-Ball** with dramatic pauses and attitude

### 🌐 **Real API Integration**
- **Weather Data** from OpenWeatherMap
- **Random Facts** from multiple sources
- **Jokes API** integration (she'll act like they're stupid)
- **Cat Facts** (she secretly loves them)

### 💝 **Relationship System**
- **Progressive Friendship**: Stranger → Acquaintance → Friend → Close Friend
- **Interaction Tracking**: Remembers every conversation
- **Personalized Responses**: Different reactions based on relationship level
- **Persistent Data**: Saves relationship progress automatically

### 🛠️ **Server Management**
- **Role Management**: Create, assign, and remove roles
- **Channel Creation**: Text and voice channels
- **User Moderation**: Kick users with tsundere attitude
- **Message Relay**: Send messages to specific channels

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Discord Bot Token
- Google Gemini API Key

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/coff33ninja/AI-discord.git
cd AI-discord
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
Create a `.env` file with:
```env
DISCORD_TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_gemini_api_key
# 🆕 Optional: Additional API keys for rotation
GEMINI_API_KEY_2=your_second_gemini_api_key
GEMINI_API_KEY_3=your_third_gemini_api_key
OPENWEATHER_API_KEY=your_weather_api_key  # Optional
```

4. **Run the bot:**
```bash
python bot.py
```

## 🎯 Commands

### 🤖 **AI & Social**
| Command | Description | Example |
|---------|-------------|---------|
| `!ai <question>` | Ask Coffee anything | `!ai What's the weather like?` |
| `!help_ai` | Show all commands | `!help_ai` |
| `!compliment` | Compliment Coffee (watch her get flustered!) | `!compliment` |
| `!mood` | Check Coffee's current mood | `!mood` |
| `!relationship` | See your friendship level | `!relationship` |

### 🔍 **🆕 Search**
| Command | Description | Example |
|---------|-------------|---------|
| `!search <query>` | Search the web with DuckDuckGo | `!search ESP32 tutorial` |
| `!websearch <query>` | Alternative web search method | `!websearch Python tips` |

### 🛠️ **Utilities**
| Command | Description | Example |
|---------|-------------|---------|
| `!time` | Current time with attitude | `!time` |
| `!calc <math>` | Calculator with tsundere responses | `!calc 2+2*3` |
| `!dice [sides]` | Roll dice (default 6 sides) | `!dice 20` |
| `!flip` | Flip a coin | `!flip` |
| `!weather <city>` | Real weather data | `!weather Tokyo` |
| `!fact` | Random interesting facts | `!fact` |
| `!joke` | Random jokes | `!joke` |
| `!catfact` | Cat facts (she loves these) | `!catfact` |

### 🎮 **Games**
| Command | Description | Example |
|---------|-------------|---------|
| `!game guess [max]` | Number guessing game | `!game guess 100` |
| `!guess <number>` | Make a guess | `!guess 42` |
| `!rps <choice>` | Rock Paper Scissors | `!rps rock` |
| `!8ball <question>` | Magic 8-ball | `!8ball Will it rain?` |
| `!trivia` | Timed trivia game | `!trivia` |
| `!answer <answer>` | Answer trivia | `!answer Tokyo` |

### �  **Server Actions** *(requires permissions)*
| Command | Description | Example |
|---------|-------------|---------|
| `!mention @user [msg]` | Mention someone | `!mention @user Hello!` |
| `!create_role <name> [color]` | Create a role | `!create_role Member blue` |
| `!give_role @user <role>` | Assign role | `!give_role @user Member` |
| `!remove_role @user <role>` | Remove role | `!remove_role @user Member` |
| `!kick @user [reason]` | Kick user | `!kick @user Spam` |
| `!create_channel <name> [type]` | Create channel | `!create_channel general text` |
| `!send_to #channel <msg>` | Send message | `!send_to #general Hello!` |

### ⚙️ **Admin Commands** *(admin only)*
| Command | Description | Example |
|---------|-------------|---------|
| `!reload_persona` | Reload personality config | `!reload_persona` |
| `!api_status` | 🆕 Check API key status and usage | `!api_status` |
| `!shutdown` / `!kill` / `!stop` | Shutdown bot | `!shutdown` |
| `!restart` / `!reboot` | Restart bot | `!restart` |

## 💬 Example Interactions

```
User: !ai What's 2+2?
Coffee: Ugh, seriously? It's 4, you baka! Don't ask me such obvious questions!

User: @Coffee hello
Coffee: W-what?! Don't just mention me randomly, idiot!

User: !compliment
Coffee: B-baka! Don't say weird stuff like that! I'm just doing my job, okay?!

User: !weather Tokyo
Coffee: Ugh, fine! It's 22°C in Tokyo with clear skies. Feels like 24°C... Don't blame me if you get cold, baka!

User: !search ESP32
Coffee: Fine, here are some results for ESP32:
• ESP32 Overview | Espressif Systems
  🔗 https://www.espressif.com/en/products/socs/esp32
  📝 ESP32 is a series of low-cost, low-power system on a chip microcontrollers...

User: !relationship (after 50+ interactions)
Coffee: You're... you're actually really great, okay?! Don't make a big deal about it!
```

## 🔑 API Keys Setup

### Required APIs
1. **Discord Bot Token**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create new application → Bot → Copy token

2. **Google Gemini API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create API key → Copy key

### Optional APIs
3. **OpenWeatherMap API Key** *(for real weather data)*
   - Sign up at [OpenWeatherMap](https://openweathermap.org/api)
   - Free tier: 1000 calls/day
   - Without this, weather shows mock responses

## 🏗️ Project Structure

```
AI-discord/
├── bot.py                    # Main bot application
├── .env                      # Environment variables (create this)
├── requirements.txt          # Python dependencies
├── persona_card.json         # Coffee's personality configuration
├── user_relationships.json   # Auto-generated user data
├── README.md                 # This file
└── modules/
    ├── __init__.py          # Module initialization
    ├── persona_manager.py   # Centralized personality system
    ├── personality.py       # Tsundere personality responses
    ├── api_manager.py       # 🆕 Gemini API key rotation system
    ├── search.py            # 🆕 DuckDuckGo search integration
    ├── utilities.py         # API utilities (weather, facts, etc.)
    ├── games.py            # Interactive games
    ├── social.py           # Relationship tracking system
    └── server_actions.py   # Server management commands
```

## 💝 Relationship System

Coffee remembers every user and builds relationships over time:

| Level | Interactions | Behavior |
|-------|-------------|----------|
| **Stranger** | 0-4 | Cold and distant, very tsundere |
| **Acquaintance** | 5-19 | Slightly warmer but still defensive |
| **Friend** | 20-49 | More caring but denies it strongly |
| **Close Friend** | 50+ | Very caring but extremely flustered |

Relationship data is automatically saved to `user_relationships.json` and persists between bot restarts.

## �️ Bot Management

### Running the Bot

**Simple Run:**
```bash
python bot.py
```

**Windows Batch Script:**
```bash
# Double-click or run in terminal
run_bot.bat
```

**Development Mode (Auto-restart on changes):**
```bash
# Install watchdog first: pip install watchdog
python dev_bot.py
# Or use: dev_bot.bat
```

### Stopping the Bot
1. **Ctrl+C** in terminal (graceful shutdown)
2. **Close terminal window** (force stop)
3. **Discord command**: `!shutdown` or `!kill` (admin only)
4. **Discord restart**: `!restart` or `!reboot` (admin only)

### Development Tips
- Use `dev_bot.py` for development - it auto-restarts when you modify files
- Use `!reload_persona` to reload personality changes without restarting
- 🆕 Use `!api_status` to monitor API key health and usage
- The bot saves user relationship data automatically
- Check logs in terminal for debugging information

## 🔧 Bot Permissions

Ensure your bot has these Discord permissions:
- ✅ Send Messages
- ✅ Read Message History  
- ✅ Embed Links
- ✅ Attach Files
- ✅ Use External Emojis
- ✅ Manage Roles *(for server actions)*
- ✅ Manage Channels *(for server actions)*
- ✅ Kick Members *(for moderation)*

## 🎨 Customization

Coffee's personality is fully customizable through `persona_card.json`:
- **Response templates** for different situations
- **Speech patterns** and common phrases
- **Relationship-specific** responses
- **Activity responses** for games, utilities, etc.
- 🆕 **Search responses** for web search results

## 🐛 Troubleshooting

### Common Issues
1. **Bot not responding**: Check Discord token and bot permissions
2. **AI not working**: Verify Gemini API key is correct
3. **🆕 API rate limits**: Add multiple API keys or check `!api_status`
4. **🆕 Search not working**: Check internet connectivity and console output
5. **Weather not working**: Add OpenWeatherMap API key or ignore (uses mock data)
6. **Permission errors**: Ensure bot has required server permissions

### Error Handling
Coffee handles errors gracefully with tsundere flair:
- API timeouts (30-second limit)
- 🆕 Automatic API key rotation on failures
- Missing permissions
- Invalid commands
- Network issues

## 🆕 New Features in Latest Update

### � Web Search Integration
- **DuckDuckGo Search** - Search the web with `!search` command
- **Instant Answers** - Quick facts, calculations, and definitions
- **Smart Parsing** - BeautifulSoup-powered result extraction
- **Tsundere Results** - All search results delivered with personality

### 🔑 Advanced API Management
- **Multiple API Keys** - Add backup keys for better reliability
- **Automatic Rotation** - Seamless failover when rate limits hit
- **Usage Monitoring** - Track requests, errors, and cooldowns
- **Admin Dashboard** - Real-time status with `!api_status`

### 🛠️ Enhanced Architecture
- **Modular Design** - Clean separation of concerns
- **Robust Error Handling** - Graceful degradation on failures
- **Production Ready** - Professional-grade HTML parsing and API management

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Coffee might act annoyed about it, but she secretly appreciates the help!

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for the intelligent conversation capabilities
- **🆕 DuckDuckGo** for search functionality
- **Discord.py** for the excellent Discord API wrapper
- **🆕 BeautifulSoup** for HTML parsing
- **OpenWeatherMap** for weather data
- Various free APIs for facts, jokes, and cat facts

---

*"I-it's not like I wanted you to star this repository or anything, baka!"* - Coffee 💕