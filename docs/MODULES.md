# Module Documentation

Complete documentation of all bot modules organized by category.

## Core Modules

### API & AI Integration
- **[api_manager.py](./modules/api_manager.md)** - Google Gemini API integration, request handling, rate limiting
- **[knowledge_manager.py](./modules/knowledge_manager.md)** - Knowledge base management, fact storage and retrieval

### Database & Persistence
- **[ai_database.py](./modules/ai_database.md)** - SQLite database operations, conversation history, user data storage

### Configuration & Personality
- **[config_manager.py](./modules/config_manager.md)** - Bot configuration management, settings persistence
- **[persona_manager.py](./modules/persona_manager.md)** - Personality/persona system, character traits and responses
- **[personality.py](./modules/personality.py.md)** - Personality trait system, mood tracking, relationship levels

### Utilities & Helpers
- **[utilities.py](./modules/utilities.md)** - Helper functions, text processing, formatting
- **[logger.py](./modules/logger.md)** - Logging configuration and management
- **[response_handler.py](./modules/response_handler.md)** - Discord embed creation, message formatting, rich responses
- **[bot_name_service.py](./modules/bot_name_service.md)** - Bot name resolution and management

## Feature Modules

### User Interaction
- **[social.py](./modules/social.md)** - Relationship tracking, friendship levels, user interactions
- **[games.py](./modules/games.md)** - Game implementations (guessing, rock-paper-scissors, trivia, 8-ball)

### Information & Search
- **[search.py](./modules/search.md)** - Web search integration (DuckDuckGo), web scraping

### Time Management
- **[time_utilities.py](./modules/time_utilities.md)** - Time operations, reminders, scheduling

### Server Management
- **[server_actions.py](./modules/server_actions.md)** - Role creation/assignment, channel management, user moderation

### Voice Features
- **[stt_manager.py](./modules/stt_manager.md)** - Speech-to-text using OpenAI Whisper
- **[tts_manager.py](./modules/tts_manager.md)** - Text-to-speech using KittenTTS
- **[voice_channel.py](./modules/voice_channel.md)** - Discord voice channel management
- **[ai_voice_integration.py](./modules/ai_voice_integration.md)** - AI-to-voice bridge, full integration
- **[voice_interaction.py](./modules/voice_interaction.md)** - Complete voice conversation pipeline (STT → AI → TTS)
- **[voice_examples.py](./modules/voice_examples.md)** - Example voice commands and usage

## Quick Module Overview

```
Core Functions
├── API & AI
│   ├── api_manager.py (Gemini integration)
│   └── knowledge_manager.py (Knowledge base)
├── Database
│   └── ai_database.py (SQLite persistence)
└── Configuration
    ├── config_manager.py (Settings)
    ├── persona_manager.py (Personality)
    └── personality.py (Traits & moods)

Features
├── User Interaction
│   ├── social.py (Relationships)
│   └── games.py (Games)
├── Information
│   └── search.py (Web search)
├── Time
│   └── time_utilities.py (Reminders)
├── Server
│   └── server_actions.py (Admin)
└── Voice
    ├── stt_manager.py (Speech recognition)
    ├── tts_manager.py (Voice synthesis)
    ├── voice_channel.py (Voice channels)
    ├── ai_voice_integration.py (Integration)
    └── voice_interaction.py (Full pipeline)

Utilities
├── utilities.py (Helpers)
├── logger.py (Logging)
├── response_handler.py (Formatting)
└── bot_name_service.py (Bot name)
```

## How to Use This Documentation

1. **Find your module** in the list above
2. **Click the link** to view detailed documentation
3. **Each module document includes:**
   - Overview and purpose
   - Key classes and functions
   - Usage examples
   - Configuration options
   - Dependencies

## Related Documentation

- **[Commands Reference](./commands.md)** - All `!` commands with examples
- **[Voice Integration](./voice/)** - Detailed voice setup and usage
- **[Setup Guides](./setup/)** - Installation and configuration

---

*Each module contains detailed docstrings in the source code. Use Python's `help()` or IDE tooltips for quick reference.*
