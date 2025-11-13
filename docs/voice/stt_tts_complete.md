# Complete Voice Interaction Guide

## Overview

The Discord bot now has full bidirectional voice communication:
1. **User speaks** in voice channel → Whisper transcribes to text
2. **Text sent to Gemini AI** → AI generates intelligent response
3. **Response synthesized with KittenTTS** → Bot speaks back to user

This creates a natural conversation where users can have hands-free discussions with the AI.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Voice Interaction Pipeline                      │
└─────────────────────────────────────────────────────────────┘
                              
User Speaks                 Bot Processing              Bot Responds
     │                            │                          │
     v                            v                          v
  Audio                   Whisper (STT)               KittenTTS (TTS)
  Input       ──────>    Transcription     ────>    Voice Output
                              │                          ▲
                              v                          │
                        Gemini AI API
                      (Response Generation)
```

### Components

1. **stt_manager.py** - Speech-to-Text using OpenAI Whisper
2. **tts_manager.py** - Text-to-Speech using KittenTTS
3. **voice_channel.py** - Discord voice channel management
4. **ai_voice_integration.py** - AI connection to voice system
5. **voice_interaction.py** - Complete conversation pipeline (NEW)
6. **api_manager.py** - Gemini AI integration

---

## Setup

### 1. Install Dependencies

All dependencies are installed:
```bash
pip install -r requirements.txt
```

This includes:
- `discord.py` - Discord bot framework
- `openai-whisper` - Speech-to-text
- `google-generativeai` - Gemini AI
- `soundfile` & `numpy` - Audio processing
- KittenTTS wheel (manual installation)

### 2. KittenTTS Wheel Installation

If not already installed:
```bash
python -m pip install https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl
```

### 3. Environment Variables

Required in `.env`:
```
DISCORD_TOKEN=your_bot_token
GEMINI_API_KEY=your_gemini_api_key
```

---

## Voice Commands

### Join/Leave Voice Channel

```
!join_voice
  → Bot joins your voice channel
  
!leave_voice
  → Bot leaves voice channel
```

### Voice Conversation

```
!listen
  → Bot starts listening to voice channel
  → Bot transcribes speech and generates responses
  
!stop_listening
  → Stops listening mode
```

### Voice History

```
!voice_history
  → Shows recent conversation history
  
!clear_voice_history
  → Clears conversation history
```

### Other Voice Commands

```
!speak <text>
  → Bot says specific text in voice channel
  
!voice_ask <question>
  → Ask a question and get voice response
  
!ai_voice
  → Toggle auto-speak on mentions
  
!toggle_auto_speak
  → Enable/disable speaking when mentioned
```

---

## How to Use

### Basic Voice Conversation Flow

1. **Start**: `!join_voice` - Bot joins your voice channel
2. **Listen**: `!listen` - Bot ready to hear you
3. **Speak**: Say something clearly (e.g., "What time is it?")
4. **Wait**: Bot transcribes and processes...
5. **Respond**: Bot speaks AI response back to you
6. **Repeat**: Continue talking for natural conversation
7. **Stop**: `!stop_listening` when done

### Example Conversation

```
User: "!join_voice"
Bot: Joins voice channel

User: "!listen"
Bot: 🎤 Listening to voice channel...

User: (speaks) "What's the weather like?"
Bot: Transcribes: "What's the weather like?"
Bot: Generates: "I don't have real-time weather data, but..."
Bot: Speaks response: "I don't have real-time weather data, but..."

User: (speaks) "Tell me a joke"
Bot: Transcribes: "Tell me a joke"
Bot: Speaks: "Why did the AI go to school?..."
```

---

## Whisper Model Sizes

The STT system can use different Whisper models:

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| tiny | 40MB | Fastest | Good | Real-time, limited quality |
| base | 140MB | Fast | Very Good | Default, balanced |
| small | 465MB | Normal | Excellent | Higher quality needed |
| medium | 1.5GB | Slower | Excellent | Clean audio |
| large | 2.9GB | Slowest | Best | Professional quality |

**Default**: `base` model (140MB, fast, accurate)

To change model in code:
```python
stt_manager = get_stt_manager()
stt_manager.load_model('small')  # Load small model instead
```

---

## Voice Interaction Class Usage

### For Developers

```python
from modules.voice_interaction import VoiceConversation
from modules.api_manager import GeminiAPIManager

# Create conversation manager
guild_id = 12345
api_manager = GeminiAPIManager()
conversation = VoiceConversation(guild_id, api_manager=api_manager)

# Process user audio
result = await conversation.process_audio_and_respond(
    audio_data=audio_bytes,
    language='en'  # Optional
)

# Result contains:
# - transcription: What user said
# - response: AI's response
# - status: success/error/partial_success/no_speech
# - error: Error message if any
print(f"User said: {result['transcription']}")
print(f"AI responded: {result['response']}")

# Access history
history = conversation.get_conversation_history()
print(f"Conversation: {history}")

# Clear history
conversation.clear_history()
```

---

## Configuration in bot.py

To enable voice interaction in your bot:

```python
from modules.voice_interaction import setup as setup_voice_interaction
from modules.api_manager import GeminiAPIManager

# In your bot setup:
api_manager = GeminiAPIManager()

# Load voice commands
await setup_voice_interaction(bot, api_manager)
```

The bot already includes:
- Auto-speak on mentions
- 6 voice commands
- Voice initialization on startup
- Per-guild voice management

---

## Troubleshooting

### Bot Won't Join Voice
```
Error: "Bot must be in a voice channel first"
→ Use !join_voice first
→ Check bot has "Connect" and "Speak" permissions in voice channel
```

### No Speech Detected
```
Status: 'no_speech' with error "No speech detected in audio"
→ Speak louder
→ Reduce background noise
→ Move closer to microphone
```

### Transcription is Inaccurate
```
Problem: Whisper misunderstanding words
Solutions:
  1. Speak more clearly
  2. Reduce background noise
  3. Use larger Whisper model (small/medium/large)
  4. Specify language: await transcribe_audio(audio, language='en')
```

### Voice Response Doesn't Play
```
Status: 'partial_success' with "Not connected to voice channel"
→ Ensure bot is in voice channel: !join_voice
→ Check bot has "Speak" permission
```

### Whisper Takes Too Long
```
Problem: Slow transcription
Solutions:
  1. Use smaller model: tiny or base (default)
  2. Increase chunk size (trades accuracy for speed)
  3. Reduce audio duration (shorter clips = faster processing)
```

### API Rate Limit
```
Error: "API rate limit exceeded"
→ Add delay between requests
→ Check Gemini API quota
→ Reduce conversation frequency
```

---

## Performance Tips

1. **Use base Whisper model** - Fast and accurate enough
2. **Keep audio clips short** - Easier to transcribe
3. **Enable noise filtering** - Improve accuracy
4. **Batch process** - Group related questions together
5. **Cache responses** - For common questions

---

## Security Considerations

1. **Audio privacy** - Audio transcribed immediately, not stored
2. **API keys** - Keep in `.env`, never commit to repo
3. **Guild isolation** - Conversations per-guild only
4. **Content moderation** - Consider content filtering for responses

---

## Conversation History

Each guild maintains its own conversation history:

```python
# Get history
history = conversation.get_conversation_history()
# Returns: [
#   {"role": "user", "content": "Hello"},
#   {"role": "assistant", "content": "Hi there!"},
#   ...
# ]

# Clear history
conversation.clear_history()

# Get length
count = conversation.get_history_length()
```

History is used for:
- Context in multi-turn conversations
- Debugging transcription issues
- Improving response accuracy
- Tracking conversation flow

---

## Advanced: Custom Audio Processing

For future enhancements:

```python
# 1. Noise suppression
# 2. Audio normalization
# 3. Silence detection
# 4. Automatic speech separation (isolate voice from background)
# 5. Voice activity detection (know when user is done talking)
```

These can be added to voice_channel.py as preprocessing.

---

## API Rate Limits

### Gemini API
- Rate varies by plan
- Check: https://ai.google.dev/pricing

### Whisper (Local)
- No rate limits (runs locally)
- Limited by hardware

---

## Files Modified/Created

**New Files:**
- `modules/voice_interaction.py` - Complete conversation pipeline
- `modules/stt_manager.py` - Speech-to-text manager

**Modified Files:**
- `bot.py` - Added voice commands and initialization
- `requirements.txt` - Added Whisper dependency

**Existing Modules:**
- `modules/tts_manager.py` - Text-to-speech
- `modules/voice_channel.py` - Voice channel management
- `modules/ai_voice_integration.py` - AI voice bridge

---

## Next Steps

1. ✅ Test voice commands: `!join_voice` → `!listen`
2. ✅ Verify transcription quality
3. ✅ Check voice response synthesis
4. ✅ Test multi-turn conversations
5. Consider adding:
   - Silence detection for auto-stop
   - Noise suppression
   - Language detection
   - Voice mood/emotion detection

---

## Support

For issues:
1. Check logs in `bot.log`
2. Test individual modules in isolation
3. Verify Gemini API key and permissions
4. Check Discord bot permissions (Connect, Speak, Read Messages)
5. Review Whisper model installation

---

**Voice interaction system ready to use! 🎤🤖🔊**
