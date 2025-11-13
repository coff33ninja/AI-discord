# Commands Reference

Complete guide to all Discord bot commands organized by category.

## 🤖 AI & Chat Commands

### Basic AI
| Command | Aliases | Usage | Description |
|---------|---------|-------|-------------|
| `!ai <question>` | `!ask`, `!chat` | `!ai What's 2+2?` | Ask the AI anything with memory and personality |
| `!memory [number]` | - | `!memory 8` | View/set conversation memory (1-10 messages) |

### Social Interaction
| Command | Aliases | Usage | Description |
|---------|---------|-------|-------------|
| `!compliment` | - | `!compliment` | Compliment the bot (watch her get flustered!) |
| `!mood` | - | `!mood` | Check the bot's current mood |
| `!relationship` | - | `!relationship` | See your friendship level with the bot |

### Help & Info
| Command | Aliases | Usage | Description |
|---------|---------|-------|-------------|
| `!help_ai` | `!commands` | `!help_ai` | Show all available commands |

---

## 🔍 Search & Information Commands

### Web Search
| Command | Aliases | Usage | Description |
|---------|---------|-------|-------------|
| `!search <query>` | `!google`, `!find` | `!search Python tips` | Search the web using DuckDuckGo |
| `!websearch <query>` | `!web` | `!websearch AI tutorial` | Alternative web search method |

### Knowledge Base
| Command | Aliases | Usage | Description |
|---------|---------|-------|-------------|
| `!factadd <key> \| <fact>` | - | `!factadd gravity \| Objects attract each other` | Add custom facts to bot's knowledge |
| `!followup <question> \| <answer>` | - | `!followup What is AI? \| AI is machine learning...` | Save Q&A pairs for reuse |
| `!follow <question>` | - | `!follow What is gravity?` | Retrieve saved Q&A or ask AI and save |

---

## 🛠️ Utility Commands

### General Utilities
| Command | Aliases | Usage | Description |
|---------|---------|-------|-------------|
| `!time` | - | `!time` | Get current time with attitude |
| `!calc <math>` | - | `!calc 2+2*3` | Calculator (supports full math expressions) |
| `!dice [sides]` | - | `!dice 20` | Roll dice (default: 6 sides) |
| `!flip` | - | `!flip` | Flip a coin (heads/tails) |
| `!stats` | - | `!stats` | View your personal usage statistics |

### Information APIs
| Command | Aliases | Usage | Description |
|---------|---------|-------|-------------|
| `!weather <city>` | - | `!weather Tokyo` | Get real weather data (requires API key) |
| `!fact` | - | `!fact` | Get random interesting facts |
| `!joke` | - | `!joke` | Get random jokes (learns your humor!) |
| `!catfact` | - | `!catfact` | Get cat facts (the bot secretly loves these) |

---

## 🎮 Game Commands

### Games
| Command | Aliases | Usage | Description |
|---------|---------|-------|-------------|
| `!game guess [max]` | - | `!game guess 100` | Start number guessing game (1-max) |
| `!guess <number>` | - | `!guess 50` | Make a guess in active game |
| `!rps <choice>` | `!rock`, `!paper`, `!scissors` | `!rps rock` | Rock Paper Scissors game |
| `!8ball <question>` | - | `!8ball Will it rain?` | Magic 8-ball (dramatic responses) |
| `!trivia` | - | `!trivia` | Start timed trivia game (30 seconds) |
| `!answer <answer>` | - | `!answer Tokyo` | Answer current trivia question |

---

## 👥 Server Management Commands
*(Requires appropriate permissions)*

### User Management
| Command | Aliases | Usage | Description |
|---------|---------|-------|-------------|
| `!mention @user [message]` | - | `!mention @user Hello!` | Mention a user with optional message |
| `!kick @user [reason]` | - | `!kick @user Spam` | Kick user from server |

### Role Management
| Command | Aliases | Usage | Description |
|---------|---------|-------|-------------|
| `!create_role <name> [color]` | - | `!create_role Member blue` | Create new server role |
| `!give_role @user <role>` | - | `!give_role @user Member` | Assign role to user |
| `!remove_role @user <role>` | - | `!remove_role @user Member` | Remove role from user |

### Channel Management
| Command | Aliases | Usage | Description |
|---------|---------|-------|-------------|
| `!create_channel <name> [type]` | - | `!create_channel general text` | Create text or voice channel |
| `!send_to #channel <message>` | - | `!send_to #general Hello!` | Send message to specific channel |

---

## ⏰ Time & Reminder Commands

### Reminders
| Command | Aliases | Usage | Description |
|---------|---------|-------|-------------|
| `!remind <time> to <message>` | - | `!remind in 5 minutes to take break` | Set a reminder (natural language) |
| `!reminders` | - | `!reminders` | List all your active reminders |
| `!cancelreminder <id>` | - | `!cancelreminder 123` | Cancel specific reminder by ID |

### Subscriptions
| Command | Aliases | Usage | Description |
|---------|---------|-------|-------------|
| `!subscribe <feature>` | - | `!subscribe daily_fact` | Subscribe to daily features |
| `!unsubscribe <feature>` | - | `!unsubscribe daily_joke` | Unsubscribe from features |
| `!subscriptions` | - | `!subscriptions` | List your active subscriptions |

**Available Features:**
- `daily_fact` - Random fact each day
- `daily_joke` - Random joke each day
- `weekly_stats` - Weekly usage stats
- `mood_checkin` - Daily mood check-in

---

## 🎤 Voice Interaction Commands
*(Beta - requires bot in voice channel)*

### Voice Setup
| Command | Aliases | Usage | Description |
|---------|---------|-------|-------------|
| `!join_voice` | - | `!join_voice` | Bot joins your voice channel |
| `!leave_voice` | - | `!leave_voice` | Bot leaves voice channel |

### Voice Interaction
| Command | Aliases | Usage | Description |
|---------|---------|-------|-------------|
| `!listen` | - | `!listen` | Start listening for speech (transcribes & responds) |
| `!stop_listening` | - | `!stop_listening` | Stop listening mode |
| `!speak <text>` | - | `!speak Hello everyone!` | Bot speaks text aloud |
| `!voice_ask <question>` | - | `!voice_ask What time is it?` | Ask question with voice response |

### Voice History
| Command | Aliases | Usage | Description |
|---------|---------|-------|-------------|
| `!voice_history` | - | `!voice_history` | Show recent conversation history |
| `!clear_voice_history` | - | `!clear_voice_history` | Clear all voice conversation history |

**See:** [Voice Integration Docs](./voice/) for full setup

---

## ⚙️ Admin Commands
*(Admin only - requires administrator permissions)*

### Configuration
| Command | Aliases | Usage | Description |
|---------|---------|-------|-------------|
| `!reload_persona` | - | `!reload_persona` | Reload personality/persona config from file |
| `!persona_health` | - | `!persona_health` | Check persona configuration for issues |
| `!persona_report` | - | `!persona_report` | Generate detailed persona validation report |

### Monitoring & Status
| Command | Aliases | Usage | Description |
|---------|---------|-------|-------------|
| `!api_status` | - | `!api_status` | Check API key status and usage stats |
| `!ai_analytics [days]` | - | `!ai_analytics 7` | View AI usage analytics for last N days |

### Bot Control
| Command | Aliases | Usage | Description |
|---------|---------|-------|-------------|
| `!shutdown` | `!kill`, `!stop` | `!shutdown` | Shutdown the bot gracefully |
| `!restart` | `!reboot` | `!restart` | Restart the bot |

---

## Command Usage Patterns

### Natural Language Commands
Some commands support natural language:

```
!remind in 5 minutes to take a break
!remind at 3:30 PM to check the oven
!remind tomorrow at 9 AM to wake up
```

### Command Aliases
Most commands have short aliases:

```
!ai question        → Same as: !ask question  or !chat question
!search query       → Same as: !google query  or !find query
!rps rock          → Same as: !rock
```

### Parameters with Spaces
Use quotes for multi-word text:

```
!speak "Hello everyone, how are you?"
!remind in 5 minutes to "finish the project"
!mention @user "Great work on that task!"
```

---

## Command Categories Reference

| Category | Command Count | Key Uses |
|----------|---------------|----------|
| AI & Chat | 4 | Ask questions, manage memory |
| Search | 3 | Web search, knowledge base |
| Utilities | 5 | Time, calculator, dice, stats |
| Games | 6 | Entertainment, interactive |
| Server Management | 7 | Admin, roles, channels, users |
| Time & Reminders | 7 | Scheduling, subscriptions |
| Voice | 8 | Voice channel interaction |
| Admin | 7 | Configuration, monitoring, control |
| **Total** | **~47** | **Full bot functionality** |

---

## Command Permission Levels

### Public Commands
Everyone can use: `!ai`, `!search`, `!weather`, `!joke`, `!dice`, `!game`, etc.

### Requires Channel Permissions
- `!send_to #channel` - Needs permission to send in target channel
- `!create_channel` - Needs channel creation permissions

### Requires Server Permissions
- `!kick @user` - Needs kick permissions
- `!create_role` - Needs role management permissions
- `!give_role` / `!remove_role` - Needs role management permissions

### Admin Commands Only
- `!reload_persona`
- `!persona_health`
- `!persona_report`
- `!api_status`
- `!ai_analytics`
- `!shutdown`
- `!restart`

---

## Error Messages & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| "Bot not in voice channel" | Can't play voice | Use `!join_voice` first |
| "No speech detected" | Nothing heard | Speak louder/clearer |
| "API rate limit" | Too many requests | Wait a moment, try again |
| "Permission denied" | Missing permissions | Check channel/server permissions |
| "Unknown command" | Typo or not recognized | Check spelling, use `!help_ai` |

---

## Tips & Tricks

1. **Use `!help_ai`** anytime to see all commands
2. **Commands are case-insensitive**: `!AI` = `!ai` = `!Ai`
3. **Aliases work**: `!ask` = `!ai` = `!chat`
4. **Set memory**: `!memory 10` for longer conversation context
5. **Check stats**: `!stats` to see your usage patterns
6. **Save facts**: Use `!factadd` to teach the bot new things
7. **Subscribe**: `!subscribe daily_fact` for daily updates
8. **Voice chat**: `!join_voice` → `!listen` for hands-free AI

---

*For detailed module documentation, see [Modules Reference](./MODULES.md)*
