# Coffee - Tsundere AI Discord Bot 🤖☕

A Discord bot with a classic tsundere personality powered by Google's Gemini AI, featuring web search capabilities and robust API key management.

## ✨ Features

### 🎭 Personality System
- **Tsundere AI Character** - Acts reluctant to help while being genuinely helpful
- **Centralized Persona Card** - All personality responses managed through `persona_card.json`
- **Relationship Tracking** - Builds relationships with users over time
- **Dynamic Responses** - AI-generated responses based on personality and relationship level

### 🔍 Search Capabilities
- **DuckDuckGo Integration** - Web search with instant answers, definitions, and abstracts
- **Dual Search Methods** - API-based instant answers + HTML parsing fallback
- **Smart Result Parsing** - BeautifulSoup-powered HTML parsing for robust results
- **Persona-Driven Responses** - All search results delivered with tsundere personality

### 🔑 Advanced API Management
- **Rotating API Keys** - Automatic rotation through multiple Gemini API keys
- **Rate Limit Handling** - Smart cooldown and retry logic
- **Usage Tracking** - Monitor requests, errors, and availability per key
- **Admin Dashboard** - Real-time API key status monitoring

### 🎮 Interactive Features
- **AI Chat** - Natural conversation with Gemini AI
- **Games** - Number guessing, rock-paper-scissors, trivia, magic 8-ball
- **Utilities** - Weather, calculator, dice, time, random facts/jokes
- **Server Management** - Role management, user actions, channel creation
- **Social System** - Relationship levels, mood tracking, compliments

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Discord Bot Token
- Google Gemini API Key(s)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd coffee-discord-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your tokens:
   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   GEMINI_API_KEY=your_primary_gemini_api_key_here
   GEMINI_API_KEY_2=your_second_gemini_api_key_here  # Optional
   GEMINI_API_KEY_3=your_third_gemini_api_key_here   # Optional
   OPENWEATHER_API_KEY=your_openweather_api_key_here # Optional
   ```

4. **Run the bot**
   ```bash
   python bot.py
   ```

### Development Mode
For auto-restart on file changes:
```bash
python dev_bot.py
```

## 📋 Commands

### 🤖 AI & Chat
- `!ai <question>` - Ask the AI anything
- `!compliment` - Give the bot a compliment (watch her get flustered!)
- `!mood` - Check the bot's current mood
- `!relationship` - See your relationship status

### 🔍 Search
- `!search <query>` - Search the web using DuckDuckGo
- `!websearch <query>` - Alternative web search method

### 🛠️ Utilities
- `!time` - Get current time
- `!calc <expression>` - Calculator
- `!dice [sides]` - Roll dice
- `!flip` - Flip a coin
- `!weather <city>` - Get weather information
- `!fact` - Random interesting fact
- `!joke` - Random joke
- `!catfact` - Random cat fact

### 🎮 Games
- `!game guess [max]` - Number guessing game
- `!guess <number>` - Make a guess
- `!rps <choice>` - Rock Paper Scissors
- `!8ball <question>` - Magic 8-ball
- `!trivia` - Start trivia game
- `!answer <answer>` - Answer trivia question

### 🔧 Server Management (with permissions)
- `!mention @user [message]` - Mention someone
- `!create_role <name> [color]` - Create a role
- `!give_role @user <role>` - Give role to user
- `!remove_role @user <role>` - Remove role from user
- `!kick @user [reason]` - Kick user
- `!create_channel <name> [type]` - Create channel
- `!send_to #channel <message>` - Send message to channel

### 👑 Admin Commands
- `!reload_persona` - Reload personality configuration
- `!api_status` - Check API key status and usage
- `!shutdown` - Shutdown the bot
- `!restart` - Restart the bot

## 🏗️ Architecture

### Core Components

```
coffee-discord-bot/
├── bot.py                 # Main bot file
├── persona_card.json      # Personality configuration
├── requirements.txt       # Dependencies
├── .env.example          # Environment template
└── modules/
    ├── personality.py     # Personality wrapper
    ├── persona_manager.py # Central personality system
    ├── api_manager.py     # Gemini API key rotation
    ├── search.py          # DuckDuckGo search integration
    ├── utilities.py       # Utility commands
    ├── games.py           # Interactive games
    ├── social.py          # Relationship tracking
    └── server_actions.py  # Server management
```

### Key Features

#### 🎭 Persona System
The bot's personality is entirely managed through `persona_card.json`, allowing for:
- Easy personality customization
- Consistent character responses
- Relationship-based interactions
- AI-generated responses that stay in character

#### 🔄 API Key Rotation
Robust API management with:
- Automatic failover between multiple API keys
- Rate limit detection and cooldown management
- Usage tracking and error monitoring
- Real-time status dashboard for admins

#### 🔍 Smart Search
Advanced search capabilities featuring:
- DuckDuckGo instant answers API
- HTML parsing fallback for comprehensive results
- BeautifulSoup-powered result extraction
- Personality-driven result presentation

## 🛠️ Configuration

### Personality Customization
Edit `persona_card.json` to customize:
- Character name and traits
- Speech patterns and responses
- Activity-specific reactions
- Relationship progression

### API Key Management
Add multiple Gemini API keys for better reliability:
```env
GEMINI_API_KEY=primary_key
GEMINI_API_KEY_2=backup_key_1
GEMINI_API_KEY_3=backup_key_2
# Add as many as needed
```

### Optional Services
- **OpenWeatherMap** - For real weather data
- **Various APIs** - Facts, jokes, trivia automatically handled

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** - For the conversational AI capabilities
- **DuckDuckGo** - For search functionality
- **Discord.py** - For Discord integration
- **BeautifulSoup** - For HTML parsing

## 🐛 Troubleshooting

### Common Issues

**Bot not responding to commands:**
- Check if the bot has proper permissions in your Discord server
- Verify your Discord token in `.env`
- Ensure the bot is online and connected

**Search not working:**
- Check internet connectivity
- Verify DuckDuckGo is accessible from your network
- Check console output for detailed error messages

**API errors:**
- Verify your Gemini API key(s) are valid
- Check API quota and usage limits
- Use `!api_status` to monitor key health

**Installation issues:**
- Ensure Python 3.8+ is installed
- Try installing dependencies individually if batch install fails
- Check for conflicting package versions

---

*It's not like I wanted you to use this bot or anything... B-baka!* 💕