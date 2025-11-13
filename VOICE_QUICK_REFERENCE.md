# AI Voice Integration - Quick Reference

## Installation Quick Start

```bash
# 1. Install KittenTTS wheel
pip install https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install FFmpeg (Windows)
winget install FFmpeg

# 4. Verify (optional)
python verify_kittentts_setup.py
```

## Voice Commands Reference

### Voice Management
| Command | Purpose | Example |
|---------|---------|---------|
| `!join_voice` | Join your voice channel | `!join_voice` |
| `!leave_voice` | Leave voice channel | `!leave_voice` |
| `!toggle_auto_speak` | Toggle voice on mentions | `!toggle_auto_speak` |

### Voice Interaction
| Command | Purpose | Example |
|---------|---------|---------|
| `!speak <text>` | Speak custom text | `!speak Hello everyone!` |
| `!voice_ask <question>` | Ask AI & hear response | `!voice_ask What is Python?` |
| `!ai_voice [name]` | Change/list voices | `!ai_voice expr-voice-3-m` |

### Voice List
```
Female Voices:
  expr-voice-2-f  (Variant 2)
  expr-voice-3-f  (Variant 3)
  expr-voice-4-f  (Variant 4)
  expr-voice-5-f  (Variant 5)

Male Voices:
  expr-voice-2-m  (Variant 2)
  expr-voice-3-m  (Variant 3)
  expr-voice-4-m  (Variant 4)
  expr-voice-5-m  (Variant 5)
```

## Quick Usage Flow

### 1. Basic Voice Interaction
```
Step 1: Join a voice channel
Step 2: Type !join_voice in Discord
Step 3: Use !speak "Hello" or !voice_ask "What is AI?"
Step 4: Bot responds with voice + text
Step 5: Type !leave_voice to disconnect
```

### 2. Automatic Mentions (Default)
```
Step 1: Join a voice channel
Step 2: Type !join_voice
Step 3: Mention the bot: @BotName Hello!
Step 4: Bot responds with text + automatically speaks
Step 5: Auto-speak can be toggled with !toggle_auto_speak
```

### 3. Change Voice
```
Step 1: Type !ai_voice to see available voices
Step 2: Type !ai_voice expr-voice-3-m (example)
Step 3: New voice takes effect immediately
```

## Architecture

```
Discord Message
    ↓
on_message() or command
    ↓
Gemini AI generates response
    ↓
↙─────────────────────→
Text Response              Voice Response
│                          │
Send to Channel      AIVoiceIntegration
│                          │
│                    TTSManager (KittenTTS)
│                          │
│                    Audio Bytes (WAV)
│                          │
│                    VoiceChannelManager
│                          │
└──────────────→ Both displayed/played
```

## Module Files

| File | Purpose | Lines |
|------|---------|-------|
| `modules/tts_manager.py` | TTS synthesis | 200 |
| `modules/voice_channel.py` | Voice channel management | 320 |
| `modules/ai_voice_integration.py` | AI ↔ Voice bridge | 380 |
| `modules/voice_examples.py` | Usage examples | 200 |
| `bot.py` | Main bot (modified) | Updated |

## Code Integration Points

### In `bot.py` - Imports
```python
from modules.ai_voice_integration import get_ai_voice_integration
```

### In `bot.py` - Initialization
```python
async def on_ready():
    global ai_voice
    ai_voice = get_ai_voice_integration(
        default_voice='expr-voice-2-f',
        auto_speak=True
    )
```

### In `bot.py` - on_message()
```python
if response:
    await message.channel.send(response)
    
    # Auto-speak in voice
    if ai_voice and ai_voice.is_connected_to_voice(message.guild.id):
        await ai_voice.speak_ai_response(message.guild.id, response)
```

### New Commands in `bot.py`
```python
@bot.command(name='speak')
async def speak_text(ctx, *, text):
    """Make AI speak in voice channel"""
    
@bot.command(name='voice_ask')
async def voice_ask_gemini(ctx, *, question):
    """Ask AI and hear response"""

@bot.command(name='ai_voice')
async def change_ai_voice(ctx, voice: str = None):
    """Change AI voice"""

# ... and more voice management commands
```

## Key Features

✨ **Automatic Voice Synthesis**
- Mentions are automatically spoken (if in voice channel)
- Toggle with `!toggle_auto_speak`

🎤 **Voice Commands**
- `!speak` - Custom text to speech
- `!voice_ask` - Ask AI and hear response

🔊 **Voice Management**
- `!join_voice` / `!leave_voice` - Control voice channel
- `!ai_voice` - Change voice/list options

📊 **Queue Management**
- Long responses split automatically
- Sequential playback of messages
- Per-guild voice settings

🔗 **Full Integration**
- Works with Gemini AI
- Stores in conversation history
- Updates relationship levels
- Works with memory system

## Performance

| Metric | Value |
|--------|-------|
| First message | ~500-1000ms |
| Subsequent | ~100-500ms |
| Model size | ~25MB |
| Queue limit | 50 messages |
| Sample rate | 24,000 Hz |

## Permissions Needed

Bot needs:
- `CONNECT` - Join voice channels
- `SPEAK` - Speak in voice channels
- `SEND_MESSAGES` - Send text responses

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Voice system not initialized" | Install KittenTTS wheel and deps |
| "Not connected to voice" | Use `!join_voice` first |
| "Failed to join" | Check bot permissions |
| "No audio" | Verify FFmpeg installed |
| "Wrong voice" | Use `!ai_voice expr-voice-2-f` |

## More Information

- **Full Guide**: See `VOICE_INTEGRATION_GUIDE.md`
- **KittenTTS Docs**: See `KITTENTTS_GUIDE.md`
- **Setup Guide**: See `KITTENTTS_SETUP.md`
- **Examples**: See `modules/voice_examples.py`

## State Summary

✅ **Fully Integrated**
- KittenTTS synthesis
- Discord voice playback
- Gemini AI responses
- Per-guild voice settings
- Auto-speak toggle
- Voice commands
- Error handling
- Queue management

Ready to use! 🚀
