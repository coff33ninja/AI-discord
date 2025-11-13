# Tsundere AI Discord Bot 🤖💕

A Discord bot with a classic tsundere personality powered by Google's Gemini AI. The bot's name and personality are fully customizable through the persona card configuration - by default, meet Akeno! She's helpful but acts annoyed about it, uses mild swearing, and gets adorably flustered when complimented!

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Discord.py](https://img.shields.io/badge/discord.py-2.3.2-blue.svg)
![Gemini AI](https://img.shields.io/badge/Gemini-2.5--flash-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🎭 Personality

The bot (Akeno by default) has a classic tsundere personality:
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
- **🆕 Conversation Memory** - Remembers previous conversations for continuity
- **🆕 Persistent Database** - SQLite storage for all AI interactions

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

### 🧠 **🆕 Memory System**
- **Conversation History**: Remembers your previous chats for context
- **User Preferences**: Learns your interests and adapts responses
- **Memory Settings**: Customize how much the bot remembers (1-10 messages)
- **Smart Context**: References past conversations naturally

### ⏰ **🆕 Time-Based Features**
- **Reminders**: Set personal reminders with natural language
- **Subscriptions**: Daily facts, jokes, weekly stats, mood check-ins
- **Persistent Scheduling**: Reminders survive bot restarts
- **Smart Notifications**: Tsundere-style pings and mentions

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
- 🆕 SQLite (included with Python - no separate installation needed)

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
DISCORD_BOT_TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_gemini_api_key
# 🆕 Optional: Additional API keys for rotation
GEMINI_API_KEY_2=your_second_gemini_api_key
GEMINI_API_KEY_3=your_third_gemini_api_key
OPENWEATHER_API_KEY=your_weather_api_key  # Optional
```

4. **🆕 Database Setup:**
The bot automatically creates its database on first run:
- Creates `data/` directory
- Initializes `ai_database.db` with all required tables
- No manual database setup required!

5. **Run the bot:**
```bash
python bot.py
```

**🆕 Development Mode (Auto-restart):**
```bash
python dev_bot.py
```

## 🎯 Commands

### 🤖 **AI & Social**
| Command | Description | Example |
|---------|-------------|---------|
| `!ai <question>` | Ask the bot anything (with memory!) | `!ai What's the weather like?` |
| `!help_ai` | Show all commands | `!help_ai` |
| `!compliment` | Compliment the bot (watch her get flustered!) | `!compliment` |
| `!mood` | Check the bot's current mood | `!mood` |
| `!relationship` | See your friendship level | `!relationship` |
| `!memory [number]` | 🆕 View/adjust conversation memory | `!memory 8` |

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
| `!fact` | Random interesting facts (personalized!) | `!fact` |
| `!joke` | Random jokes (learns your humor!) | `!joke` |
| `!catfact` | Cat facts (she loves these) | `!catfact` |
| `!stats` | 🆕 Your personal usage statistics | `!stats` |

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

### ⏰ **🆕 Time & Reminders**
| Command | Description | Example |
|---------|-------------|---------|
| `!remind <time> to <message>` | Set a reminder | `!remind in 5 minutes to take a break` |
| `!reminders` | List your active reminders | `!reminders` |
| `!cancelreminder <id>` | Cancel a specific reminder | `!cancelreminder 123` |
| `!subscribe <feature>` | Subscribe to daily features | `!subscribe daily_fact` |
| `!unsubscribe <feature>` | Unsubscribe from features | `!unsubscribe daily_joke` |
| `!subscriptions` | List your subscriptions | `!subscriptions` |

### ⚙️ **Admin Commands** *(admin only)*
| Command | Description | Example |
|---------|-------------|---------|
| `!reload_persona` | Reload personality config | `!reload_persona` |
| `!api_status` | Check API key status and usage | `!api_status` |
| `!ai_analytics [days]` | 🆕 View AI usage analytics | `!ai_analytics 7` |
| `!shutdown` / `!kill` / `!stop` | Shutdown bot | `!shutdown` |
| `!restart` / `!reboot` | Restart bot | `!restart` |

## 💬 Example Interactions

```
User: !ai What's 2+2?
Bot: Ugh, seriously? It's 4, you baka! Don't ask me such obvious questions!

User: !ai Do you remember what I just asked?
Bot: Of course I remember, idiot! You asked about 2+2 and I told you it was 4! 
     It's not like I pay attention to everything you say or anything...

User: @BotName hello
Bot: W-what?! Don't just mention me randomly, idiot!

User: !remind in 30 minutes to check the oven
Bot: Ugh, fine! I'll remind you about 'check the oven' at 3:30 PM on November 13. 
     Don't blame me if you forget anyway, baka! (Reminder ID: 1)

User: !memory 10
Bot: Fine! Your memory is now set to 10 messages. It's not like I wanted to 
     remember more of our conversations or anything, baka!

User: !stats
Bot: 📊 Your Chat Statistics:
     **Total Conversations:** 47
     **Days Active:** 3
     **Average per Day:** 15.7
     **Most Used Commands:**
     • ai: 23 times
     • joke: 8 times
     • weather: 5 times

User: !subscribe daily_fact
Bot: ✅ Fine! You're now subscribed to daily facts. Don't expect me to be excited about it!
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
├── dev_bot.py               # Development runner with auto-restart
├── .env                      # Environment variables (create this)
├── requirements.txt          # Python dependencies
├── persona_card.json         # Bot's personality and name configuration
├── user_relationships.json   # Auto-generated user data
├── README.md                 # This file
├── data/                     # 🆕 Database storage directory
│   └── ai_database.db       # 🆕 SQLite database (auto-created)
└── modules/
    ├── __init__.py          # Module initialization
    ├── persona_manager.py   # Centralized personality system
    ├── personality.py       # Tsundere personality responses
    ├── api_manager.py       # Gemini API key rotation system
    ├── search.py            # DuckDuckGo search integration
    ├── utilities.py         # 🆕 Memory-aware API utilities
    ├── games.py            # Interactive games
    ├── social.py           # Relationship tracking system
    ├── server_actions.py   # Server management commands
    ├── ai_database.py      # 🆕 Async SQLite database for AI data
    ├── time_utilities.py   # 🆕 Reminders and time-based features
    ├── config_manager.py   # Configuration management
    ├── response_handler.py # Response formatting utilities
    └── logger.py           # Logging system
```

## 💝 Relationship System

The bot remembers every user and builds relationships over time:

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

The bot's personality is fully customizable through `persona_card.json`:
- **Bot Name**: Set the `name` field to customize the bot's identity (defaults to "Discord AI" if not set)
- **Response templates** for different situations
- **Speech patterns** and common phrases
- **Relationship-specific** responses
- **Activity responses** for games, utilities, etc.
- 🆕 **Search responses** for web search results

### Dynamic Bot Name System

The bot automatically uses the name specified in the `persona_card.json` file:
- **Persona Card Name**: If `persona_card.json` exists and has a `name` field, that name is used throughout the bot
- **Fallback Name**: If no persona card exists or the name field is missing, "Discord AI" is used as the default
- **Live Updates**: Use `!reload_persona` to update the bot name without restarting
- **Consistent Identity**: The dynamic name appears in status messages, help commands, and responses

## 🐛 Troubleshooting

### Common Issues
1. **Bot not responding**: Check Discord token and bot permissions
2. **AI not working**: Verify Gemini API key is correct
3. **🆕 API rate limits**: Add multiple API keys or check `!api_status`
4. **🆕 Search not working**: Check internet connectivity and console output
5. **Weather not working**: Add OpenWeatherMap API key or ignore (uses mock data)
6. **Permission errors**: Ensure bot has required server permissions

### Error Handling
The bot handles errors gracefully with tsundere flair:
- API timeouts (30-second limit)
- 🆕 Automatic API key rotation on failures
- Missing permissions
- Invalid commands
- Network issues

## 🆕 New Features in Latest Update

### 🧠 AI Memory System
- **Conversation Memory** - The bot remembers your previous chats for natural continuity
- **User Preferences** - Learns your interests and adapts responses accordingly
- **Memory Settings** - Customize memory length (1-10 messages) with `!memory`
- **Smart Context** - References past conversations naturally in responses
- **Persistent Storage** - All conversations saved to SQLite database

### ⏰ Time-Based Features
- **Smart Reminders** - Set reminders with natural language: `!remind in 5 minutes to take a break`
- **Subscription System** - Subscribe to daily facts, jokes, weekly stats, mood check-ins
- **Persistent Scheduling** - Reminders survive bot restarts and are restored automatically
- **Tsundere Notifications** - All reminders delivered with the bot's signature attitude

### 🗄️ Advanced Database System
- **SQLite Integration** - Async database for all AI interactions and user data
- **Conversation Tracking** - Complete history of all AI conversations with metadata
- **Performance Analytics** - Track model usage, response times, and success rates
- **User Analytics** - Personal usage statistics and interaction patterns

### 🧠 Memory-Aware Utilities
- **Personalized Weather** - Remembers your favorite locations
- **Adaptive Jokes** - Learns your humor preferences from reactions
- **Contextual Facts** - Delivers facts based on your interests
- **Smart Responses** - All utilities now consider your conversation history

### 🔍 Web Search Integration
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
- **Modular Design** - Clean separation of concerns with specialized modules
- **Robust Error Handling** - Graceful degradation on failures
- **Production Ready** - Professional-grade database management and API handling
- **Memory Integration** - All systems now work together for personalized experiences

## 🚀 Future Plans & Roadmap

The bot is constantly evolving! Here are some exciting features planned for future updates:

### 🎵 **Voice Integration**
- **Text-to-Speech** - Hear the bot's tsundere voice with customizable voice models
- **Voice Commands** - Talk to the bot directly in voice channels
- **Voice Reactions** - Tsundere audio responses to voice interactions
- **Music Bot Integration** - The bot can play music while being embarrassed about it
- **Voice Reminders** - Audio notifications for your reminders

### 🎨 **Visual Enhancements**
- **Avatar Expressions** - Dynamic avatar that changes based on mood and interactions
- **Custom Emojis** - Tsundere-themed emoji reactions and responses
- **Rich Embeds** - Beautiful, themed message formatting with personality
- **Image Generation** - AI-powered tsundere artwork and memes
- **Reaction GIFs** - Animated responses for different situations

### 🧠 **Advanced AI Features**
- **Emotion Recognition** - Detect user mood from messages and adapt responses
- **Learning Conversations** - The bot learns your communication style over time
- **Multi-Language Support** - Tsundere responses in different languages
- **Context Awareness** - Understanding of ongoing conversations across channels
- **Personality Evolution** - The bot's personality develops based on server culture

### 🎮 **Enhanced Gaming**
- **RPG Elements** - Level up your relationship with the bot through adventures
- **Mini-Games Collection** - Puzzle games, word games, and challenges
- **Multiplayer Games** - Server-wide games and competitions
- **Achievement System** - Unlock special responses and features
- **Game Statistics** - Track your gaming history and achievements

### 🌐 **Smart Integrations**
- **Calendar Integration** - Sync with Google Calendar for smart reminders
- **Social Media Monitoring** - Optional Twitter/Reddit integration for trending topics
- **Smart Home Control** - Control IoT devices with tsundere attitude
- **GitHub Integration** - Code review comments with personality
- **Spotify Integration** - Music recommendations with embarrassed explanations

### 📊 **Advanced Analytics**
- **Mood Tracking** - Long-term emotional analysis and insights
- **Conversation Insights** - Detailed analysis of your chat patterns
- **Server Analytics** - Community interaction statistics for admins
- **Predictive Features** - Anticipate user needs based on patterns
- **Export Tools** - Download your conversation history and statistics

### 🔧 **Quality of Life**
- **Mobile App** - Dedicated mobile interface for bot interactions
- **Web Dashboard** - Browser-based control panel for settings and analytics
- **Backup & Sync** - Cloud backup of your relationship data
- **Custom Triggers** - Create your own automated responses and actions
- **Plugin System** - Community-developed extensions and features

### 🎭 **Personality Expansion**
- **Multiple Personas** - Switch between different character types
- **Seasonal Events** - Special holiday personalities and responses
- **Mood Variations** - Different tsundere intensities based on time/events
- **Character Development** - The bot's personality grows more complex over time
- **Interactive Backstory** - Discover the bot's history through conversations

### 🛡️ **Moderation & Safety**
- **Smart Moderation** - AI-powered content filtering with personality
- **Anti-Spam Protection** - Tsundere responses to spam attempts
- **User Reporting** - Easy reporting system with the bot as mediator
- **Parental Controls** - Family-friendly mode with adjusted personality
- **Privacy Controls** - Granular control over data collection and usage

### 🌟 **Community Features**
- **Server Leaderboards** - Relationship rankings and achievements
- **Bot Cafés** - Special channels for bot enthusiasts
- **User Testimonials** - Share your favorite bot moments
- **Community Events** - Server-wide activities and celebrations
- **Beta Testing Program** - Early access to new features

### 🔮 **Experimental Features**
- **AR Integration** - Augmented reality bot interactions
- **Blockchain Integration** - NFT achievements and collectibles (if there's demand)
- **AI Art Generation** - Custom tsundere artwork based on conversations
- **Dream Journal** - The bot remembers and discusses your shared "dreams"
- **Time Capsules** - Messages that unlock after specified time periods

---

### 🗳️ **Community Input**

Want to influence the bot's development? Here's how you can help shape her future:

- **Feature Requests** - Submit ideas via GitHub issues
- **Beta Testing** - Join our testing community for early access
- **Feedback** - Share your experiences and suggestions
- **Contributions** - Code contributions are always welcome!
- **Donations** - Support development for faster feature releases

*"I-it's not like I'm excited about these new features or anything! But... if you want to help make them happen, I guess that would be... nice. Baka!"* - Your Tsundere Bot 💕

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. The bot might act annoyed about it, but she secretly appreciates the help!

### 🛠️ **Development Priorities**

Current development focus (in order):
1. **Voice Integration** - Text-to-speech and voice commands
2. **Visual Enhancements** - Dynamic avatars and rich embeds  
3. **Advanced Gaming** - RPG elements and achievement system
4. **Smart Integrations** - Calendar and external service connections
5. **Mobile App** - Dedicated mobile interface

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

*"I-it's not like I wanted you to star this repository or anything, baka!"* - Your Tsundere Bot 💕