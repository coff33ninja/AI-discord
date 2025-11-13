# Voice Interaction Quick Reference

## Voice Commands Cheat Sheet

### Setup
| Command | Purpose |
|---------|---------|
| `!join_voice` | Bot joins your voice channel |
| `!leave_voice` | Bot leaves voice channel |

### Conversation
| Command | Purpose |
|---------|---------|
| `!listen` | Start listening for speech |
| `!stop_listening` | Stop listening |
| `!speak <text>` | Bot says specific text |
| `!voice_ask <question>` | Ask question, get voice response |

### Management
| Command | Purpose |
|---------|---------|
| `!voice_history` | Show conversation history |
| `!clear_voice_history` | Clear all history |
| `!ai_voice` | Toggle auto-speak on mentions |
| `!toggle_auto_speak` | Enable/disable speaking |

---

## Complete Voice Conversation Flow

```
1. !join_voice          ← Bot joins your voice channel
2. !listen              ← Bot starts listening
3. Speak clearly        ← Say something
4. [Processing]         ← Whisper → AI → TTS
5. Bot responds         ← You hear AI voice
6. Repeat 3-5           ← Natural conversation
7. !stop_listening      ← Stop listening
8. !leave_voice         ← Bot leaves
```

---

## What's Happening Behind the Scenes

```
User Audio Input
       ↓
   Whisper (STT)  ← Converts speech to text
       ↓
   Gemini AI      ← Generates intelligent response
       ↓
   KittenTTS      ← Converts text to speech
       ↓
  Voice Output    ← You hear the response
```

---

## System Architecture

```
voice_interaction.py (Main Pipeline)
    ├── stt_manager.py (Whisper - speech to text)
    ├── tts_manager.py (KittenTTS - text to speech)
    ├── voice_channel.py (Discord voice management)
    ├── ai_voice_integration.py (AI voice bridge)
    └── api_manager.py (Gemini AI responses)
```

---

## VoiceConversation Methods (Developers)

```python
# Create conversation manager
conversation = VoiceConversation(guild_id, api_manager=api_manager)

# Main processing
result = await conversation.process_audio_and_respond(audio_bytes)
# Returns: {
#   'transcription': 'what user said',
#   'response': 'ai response',
#   'status': 'success',
#   'error': None
# }

# History access
history = conversation.get_conversation_history()
conversation.clear_history()
length = conversation.get_history_length()

# State
conversation.is_listening  # True/False
```

---

## Common Status Values

| Status | Meaning | Action |
|--------|---------|--------|
| `success` | Complete conversation worked ✅ | Continue |
| `no_speech` | No speech detected in audio | Speak louder |
| `partial_success` | Worked but with issues ⚠️ | Check error message |
| `error` | Failed to process | Check logs |
| `processing` | Currently processing | Wait |

---

## Whisper Models

| Model | Size | Speed | Quality | Default? |
|-------|------|-------|---------|----------|
| tiny | 40MB | ⚡ | Fair | - |
| base | 140MB | Fast | Good | **YES** |
| small | 465MB | Normal | Very Good | - |
| medium | 1.5GB | Slow | Excellent | - |
| large | 2.9GB | Slow | Best | - |

---

## File Tree

```
AI-discord/
├── bot.py                           ← Main bot (has voice commands)
├── requirements.txt                 ← Dependencies
├── VOICE_INTERACTION_COMPLETE_GUIDE.md  ← Full documentation
├── VOICE_INTERACTION_QUICK_REFERENCE.md ← This file
└── modules/
    ├── stt_manager.py              ← Whisper wrapper
    ├── tts_manager.py              ← KittenTTS wrapper
    ├── voice_channel.py            ← Discord voice management
    ├── ai_voice_integration.py     ← AI voice bridge
    ├── voice_interaction.py        ← Complete pipeline
    ├── voice_examples.py           ← Example commands
    └── api_manager.py              ← Gemini AI
```

---

## Quick Troubleshooting

```
Bot won't join voice
  → Use !join_voice
  → Check bot has Connect/Speak permissions

No speech detected
  → Speak louder/clearer
  → Reduce background noise

Slow transcription
  → Use smaller Whisper model (default is fast)
  → Reduce audio length

Wrong transcription
  → Speak more slowly
  → Use larger Whisper model
  → Reduce background noise

Bot won't speak
  → Ensure bot is in voice channel
  → Check bot has Speak permission
```

---

## Dependencies Installed

✅ discord.py - Discord bot
✅ google-generativeai - Gemini AI
✅ openai-whisper - Speech recognition
✅ soundfile - Audio I/O
✅ numpy - Numerics
✅ python-dotenv - Environment variables
✅ KittenTTS - Text-to-speech (wheel)

---

## Example: Basic Usage

```python
# In your Discord command
@bot.command(name='voice_test')
async def voice_test(ctx):
    # Get conversation for this server
    conversation = VoiceConversation(
        ctx.guild.id,
        api_manager=api_manager
    )
    
    # Simulate user audio (in real use, from voice channel)
    result = await conversation.process_audio_and_respond(audio_bytes)
    
    if result['status'] == 'success':
        await ctx.send(f"You said: {result['transcription']}")
        await ctx.send(f"AI said: {result['response']}")
    else:
        await ctx.send(f"Error: {result['error']}")
```

---

## Next Steps

1. Test basic voice commands
2. Try voice conversation with AI
3. Check conversation history
4. Tune Whisper model if needed
5. Add silence detection (future)
6. Add noise suppression (future)

---

## Performance Stats

- **Whisper (base)**: ~5-10 seconds per minute of audio
- **Gemini API**: ~1-2 seconds for response
- **KittenTTS**: ~0.5-2 seconds depending on response length
- **Total**: ~7-14 seconds for full cycle (acceptable for voice chat)

---

**Ready to voice chat with your AI! 🎤🤖**
